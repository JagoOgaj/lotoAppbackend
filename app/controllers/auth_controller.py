from flask import Blueprint, jsonify
from flask_jwt_extended import (
    jwt_required,
    get_jwt_identity,
    create_access_token,
    get_jwt,
)
from app.models import User
from app.helpers import (
    revoke_token,
    add_token_to_database,
    is_token_revoked,
)
from app.extensions import jwt
from flask import current_app as app


auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    """
    Rafraîchir le jeton d'accès.

    Cette méthode permet à un utilisateur d'obtenir un nouveau jeton d'accès en utilisant un jeton de rafraîchissement valide.
    Le nouveau jeton d'accès remplace l'ancien et peut être utilisé pour accéder à des ressources protégées.

    Returns:
        tuple: Un tuple contenant un objet JSON avec le nouveau jeton d'accès et un code de statut HTTP.
            - En cas de succès (201):
                - 'access_token': Le nouveau jeton d'accès généré.
            - En cas d'erreur (422):
                - 'message': Un message indiquant qu'une erreur est survenue lors du rafraîchissement du jeton.
                - 'errors': Un booléen indiquant qu'une erreur s'est produite.
                - 'details': Des informations supplémentaires sur l'erreur (le cas échéant).

    Raises:
        Exception: Pour toute erreur inattendue qui pourrait survenir lors du processus de rafraîchissement du jeton.
    """
    try:
        user_id = get_jwt_identity()
        access_token = create_access_token(identity=user_id)
        add_token_to_database(access_token)
        return jsonify({"access_token": access_token}), 201
    except Exception as e:
        return (
            jsonify(
                {
                    "message": "une erreur est survenu dans le refresh du token",
                    "errors": True,
                    "details": str(e),
                }
            ),
            422,
        )


@auth_bp.route("/revoke_access", methods=["DELETE"])
@jwt_required()
def revoke_access_token():
    """
    Révoquer le jeton d'accès de l'utilisateur.

    Cette méthode permet à un utilisateur de révoquer son jeton d'accès actuel. Une fois révoqué, ce jeton ne peut plus
    être utilisé pour accéder à des ressources protégées.

    Returns:
        tuple: Un tuple contenant un objet JSON avec un message de confirmation et un code de statut HTTP.
            - En cas de succès (200):
                - 'message': Un message indiquant que le jeton a été révoqué avec succès.
            - En cas d'erreur (422):
                - 'message': Un message indiquant qu'une erreur s'est produite lors de la révocation du jeton.
                - 'errors': Un booléen indiquant qu'une erreur s'est produite.
                - 'details': Des informations supplémentaires sur l'erreur (le cas échéant).

    Raises:
        Exception: Pour toute erreur inattendue qui pourrait survenir lors du processus de révocation du jeton.
    """
    try:
        jti = get_jwt()["jti"]
        user_id = get_jwt_identity()
        revoke_token(jti, user_id)
        return jsonify({"message": "Token revoked"}), 200
    except Exception as e:
        return (
            jsonify(
                {"message": "Failed to revoke token", "errors": True, "details": str(e)}
            ),
            422,
        )


@auth_bp.route("/revoke_refresh", methods=["DELETE"])
@jwt_required(refresh=True)
def revoke_refresh_token():
    """
    Révoquer le jeton de rafraîchissement de l'utilisateur.

    Cette méthode permet à un utilisateur de révoquer son jeton de rafraîchissement actuel. Une fois révoqué,
    ce jeton ne pourra plus être utilisé pour générer de nouveaux jetons d'accès.

    Returns:
        tuple: Un tuple contenant un objet JSON avec un message de confirmation et un code de statut HTTP.
            - En cas de succès (200):
                - 'message': Un message indiquant que le jeton de rafraîchissement a été révoqué avec succès.
            - En cas d'erreur (422):
                - 'message': Un message indiquant qu'une erreur s'est produite lors de la révocation du jeton.
                - 'errors': Un booléen indiquant qu'une erreur s'est produite.
                - 'details': Des informations supplémentaires sur l'erreur (le cas échéant).

    Raises:
        Exception: Pour toute erreur inattendue qui pourrait survenir lors du processus de révocation du jeton.
    """
    try:
        jti = get_jwt()["jti"]
        user_id = get_jwt_identity()
        revoke_token(jti, user_id)
        return jsonify({"message": "Refresh token revoked"}), 200
    except Exception as e:
        return jsonify(
            {
                "message": "Une erreur est survnue dans le revoke du token",
                "errors": True,
                "details": str(e),
            }
        )


@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_headers, jwt_payload):
    """
    Vérifie si le jeton JWT a été révoqué.

    Cette fonction est utilisée par Flask-JWT-Extended pour déterminer si un jeton JWT donné a été révoqué.
    Elle est appelée chaque fois qu'une requête utilise un jeton JWT, permettant ainsi de gérer les jetons
    révoqués en les empêchant d'accéder aux ressources protégées.

    Args:
        jwt_headers (dict): Les en-têtes du jeton JWT, généralement contenant des informations sur le type de
                            jeton et sa signature.
        jwt_payload (dict): La charge utile du jeton JWT, contenant les informations d'identité de l'utilisateur
                            ainsi que des métadonnées, y compris le jeton de révocation (jti).

    Returns:
        bool:
            - True si le jeton a été révoqué, empêchant ainsi l'accès à des ressources protégées.
            - False si le jeton est valide et non révoqué.

    Raises:
        Exception: Si une erreur se produit lors de la vérification du jeton, cela renverra True, indiquant
                    que le jeton est considéré comme révoqué par défaut.
    """
    try:
        return is_token_revoked(jwt_payload)
    except Exception:
        return True


@auth_bp.route("/get-role", methods=["GET"])
@jwt_required()
def get_role():
    """
    Récupère le rôle de l'utilisateur connecté.

    Cette fonction est utilisée pour obtenir le rôle associé à l'utilisateur authentifié via un jeton JWT.
    Elle extrait l'identité de l'utilisateur du jeton, interroge la base de données pour récupérer les
    informations de l'utilisateur, puis renvoie le rôle de l'utilisateur.

    Returns:
        Response:
            - JSON contenant le nom du rôle de l'utilisateur et un code de statut HTTP 200 si l'utilisateur est trouvé.
            - JSON avec un message d'erreur et un code de statut HTTP 404 si l'utilisateur n'est pas trouvé.
            - JSON contenant des informations sur l'erreur et un code de statut HTTP 500 en cas d'erreur de traitement.

    Raises:
        Exception: Si une erreur se produit lors de l'accès à la base de données ou d'autres erreurs internes,
                    un message d'erreur sera retourné avec des détails sur l'exception.
    """
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if not user:
            return jsonify({"message": "User not found"}), 404
        return jsonify({"role": user.role_name}), 200
    except Exception as e:
        return jsonify(
            {
                "message": "une erreur est survenue dans la récupération du role",
                "errors": True,
                "details": str(e),
            }
        )


@jwt.user_lookup_loader
def user_loader_callback(jwt_headers, jwt_payload):
    """
    Charge l'utilisateur à partir des données du jeton JWT.

    Cette fonction est utilisée pour retrouver l'utilisateur associé à l'identité contenue dans le
    payload du jeton JWT. Elle est appelée automatiquement par Flask-JWT-Extended lorsqu'un jeton est
    validé et permet de récupérer l'utilisateur à partir de la base de données.

    Args:
        jwt_headers (dict): Les en-têtes du jeton JWT.
        jwt_payload (dict): Le payload du jeton JWT contenant les informations de l'utilisateur.

    Returns:
        User or None:
            - L'objet User correspondant à l'identité spécifiée dans le payload si l'utilisateur est trouvé.
            - None si l'utilisateur n'est pas trouvé dans la base de données.

    Example:
        Pour utiliser cette fonction, il suffit de l'enregistrer avec le décorateur
        @jwt.user_lookup_loader. Lorsque le jeton est validé, cette fonction sera appelée
        automatiquement pour récupérer l'utilisateur.

    Raises:
        Exception: Si une erreur se produit lors de la récupération de l'utilisateur,
                    None sera retourné sans lever d'exception.
    """
    identity = jwt_payload[app.config["JWT_IDENTITY_CLAIM"]]
    return User.query.get(identity)
