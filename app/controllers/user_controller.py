from flask import jsonify, request, Blueprint
from marshmallow import ValidationError
from app.schemas import (
    UserLoginSchema,
    UserCreateSchema,
    UserOverviewInfoSchema,
    UserUpdateSchema,
    UserPasswordUpdateSchema,
    EntryRegistrySchema,
    LotteryHistorySchema,
    LotteryOverviewSchema,
    LotteryWinerSchema,
)
from app.models import User, Entry, Lottery, LotteryResult, LotteryRanking
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
    get_jwt,
    get_current_user,
)
from app.extensions import db, pwd_context
from app.helpers import add_token_to_database, revoke_token
from app.tools.status_tools import Status
from datetime import datetime

user_bp = Blueprint("user", __name__)


@user_bp.route("/login", methods=["POST"])
def login_user():
    """
    Authentifie un utilisateur et génère des tokens d'accès et de rafraîchissement.

    Cette fonction permet aux utilisateurs de se connecter en fournissant leur adresse email
    et leur mot de passe. Si les informations sont valides, elle génère un token d'accès et un
    token de rafraîchissement pour l'utilisateur, qui peuvent être utilisés pour accéder à des
    ressources protégées.

    Returns:
        Response:
            - Si l'authentification réussit, renvoie un message de succès avec les tokens.
            - Si l'utilisateur n'est pas trouvé, renvoie un message d'erreur 404.
            - Si le mot de passe est incorrect, renvoie un message d'erreur 401.
            - Si une erreur de validation se produit, renvoie un message d'erreur 400 avec des détails.

    Example:
        Pour utiliser cette fonction, envoyez une requête POST à l'URL `/login`
        avec un corps JSON contenant les champs suivants :

        {
            "email": "user@example.com",
            "password": "votre_mot_de_passe"
        }

    Raises:
        ValidationError: Si les données de connexion ne respectent pas le schéma défini.
        Exception: Pour toutes les autres erreurs survenant lors du processus de connexion.
    """
    try:
        data = request.get_json()

        schema = UserLoginSchema()
        data = schema.load(data)

        email = data.get("email")
        password = data.get("password")

        user = User.query.filter_by(_email=email, _role_id=2).one_or_none()
        if not user:
            return (
                jsonify({"message": "Aucun utilisateur trouvé", "errors": True}),
                404,
            )

        if not pwd_context.verify(password, user.password_hash):
            return (
                jsonify({"message": "Mot de passe incorrect", "errors": True}),
                401,
            )

        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)

        add_token_to_database(access_token)
        add_token_to_database(refresh_token)

        return (
            jsonify(
                {
                    "message": "Utilisateur trouvé avec succès.",
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                }
            ),
            201,
        )

    except ValidationError as err:
        return (
            jsonify(
                {
                    "errors": True,
                    "message": "Erreur de validation des champs",
                    "details": err.messages,
                }
            ),
            400,
        )

    except Exception as e:
        return (
            jsonify(
                {
                    "message": str(e),
                    "errors": True,
                }
            ),
            400,
        )


@user_bp.route("/register", methods=["POST"])
def register_user():
    """
    Enregistre un nouvel utilisateur dans le système.

    Cette fonction permet à un nouvel utilisateur de s'inscrire en fournissant
    ses informations personnelles. Si l'email est déjà utilisé, un message d'erreur
    est renvoyé. Si l'inscription est réussie, un utilisateur est créé dans la base
    de données et des tokens d'accès et de rafraîchissement sont générés pour l'utilisateur.

    Returns:
        Response:
            - Si l'inscription réussit, renvoie un message de succès avec les tokens.
            - Si l'email est déjà utilisé, renvoie un message d'erreur 400.
            - Si une erreur de validation se produit, renvoie un message d'erreur 400 avec des détails.
            - Si une autre erreur se produit, renvoie un message d'erreur 500.

    Example:
        Pour utiliser cette fonction, envoyez une requête POST à l'URL `/register`
        avec un corps JSON contenant les champs suivants :

        {
            "first_name": "Prénom",
            "last_name": "Nom",
            "email": "user@example.com",
            "password": "votre_mot_de_passe"
        }

    Raises:
        ValidationError: Si les données d'inscription ne respectent pas le schéma défini.
        Exception: Pour toutes les autres erreurs survenant lors du processus d'inscription.
    """
    try:
        data = request.get_json()
        schema = UserCreateSchema()
        data = schema.load(data)

        if User.query.filter_by(_email=data["email"]).first():
            return (
                jsonify(
                    {
                        "errors": True,
                        "message": "L'email est déjà utilisé.",
                    }
                ),
                400,
            )

        new_user = User(
            _first_name=data["first_name"],
            _last_name=data["last_name"],
            _email=data["email"],
            _password_hash=pwd_context.hash(data["password"]),
            _role_id=2,
        )

        db.session.add(new_user)
        db.session.commit()

        access_token = create_access_token(identity=new_user.id)
        refresh_token = create_refresh_token(identity=new_user.id)

        add_token_to_database(access_token)
        add_token_to_database(refresh_token)

        return (
            jsonify(
                {
                    "message": "Utilisateur créé avec succès.",
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                }
            ),
            201,
        )

    except ValidationError as err:
        return (
            jsonify(
                {
                    "errors": True,
                    "message": "Erreur de validation des champs",
                    "details": err.messages,
                }
            ),
            400,
        )

    except Exception as e:
        return (
            jsonify(
                {
                    "errors": True,
                    "message": "Une erreur est survenue",
                    "details": str(e),
                }
            ),
            500,
        )


@user_bp.route("/account-info", methods=["GET"])
@jwt_required()
def account_info():
    """
    Récupère les informations du compte de l'utilisateur connecté.

    Cette fonction vérifie si l'utilisateur est connecté et récupère ses
    informations de compte, telles que le prénom, le nom, l'email et les
    préférences de notification. Les informations sont renvoyées sous
    forme de JSON.

    Returns:
        Response:
            - 200 OK: Si les informations de l'utilisateur sont récupérées avec succès.
            - 404 Not Found: Si aucun utilisateur n'est trouvé pour l'identité fournie.
            - 400 Bad Request: En cas d'erreur de validation lors de la récupération des informations.
            - 500 Internal Server Error: Pour toute autre erreur survenant lors du traitement.

    Example:
        Pour utiliser cette fonction, envoyez une requête GET à l'URL `/account-info`
        avec un token JWT valide dans l'en-tête d'autorisation. La réponse contiendra
        les informations de compte de l'utilisateur au format JSON :

        {
            "first_name": "Prénom",
            "last_name": "Nom",
            "email": "user@example.com",
            "notification": true
        }

    Raises:
        ValidationError: Si les données récupérées ne respectent pas le schéma défini.
        Exception: Pour toutes les autres erreurs survenant lors de la récupération des informations.
    """
    try:
        user = get_current_user()
        if not user:
            return (
                jsonify({"message": "Aucun utilisateur trouvé", "errors": True}),
                404,
            )

        userOverviewInfo = UserOverviewInfoSchema()
        user_data = userOverviewInfo.dump(
            {
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
                "notification": user.notification,
            }
        )

        return jsonify(user_data)
    except ValidationError as err:
        return (
            jsonify(
                {
                    "errors": True,
                    "message": "Erreur de récupération des informations",
                    "details": err.messages,
                }
            ),
            400,
        )
    except Exception as e:
        return (
            jsonify(
                {
                    "errors": True,
                    "message": "Une erreur est survenue",
                    "details": str(e),
                }
            ),
            500,
        )


@user_bp.route("/update-info", methods=["PUT"])
@jwt_required()
def update_info():
    """
    Met à jour les informations du compte de l'utilisateur connecté.

    Cette fonction permet à l'utilisateur de mettre à jour ses informations
    de compte, y compris le prénom, le nom, l'email et les préférences de
    notification. Les nouvelles données doivent être envoyées au format JSON
    dans le corps de la requête. Les mises à jour ne se produiront que si
    les champs correspondants sont inclus dans la demande.

    Returns:
        Response:
            - 200 OK: Si les informations de l'utilisateur ont été mises à jour avec succès.
            - 404 Not Found: Si aucun utilisateur n'est trouvé pour l'identité fournie.
            - 400 Bad Request: En cas d'erreur de validation lors de la mise à jour des informations.
            - 500 Internal Server Error: Pour toute autre erreur survenant lors du traitement.

    Example:
        Pour utiliser cette fonction, envoyez une requête PUT à l'URL `/update-info`
        avec un token JWT valide dans l'en-tête d'autorisation et des données JSON dans
        le corps de la requête, par exemple :

        {
            "first_name": "NouveauPrénom",
            "last_name": "NouveauNom",
            "email": "nouveau_email@example.com",
            "notification": false
        }

        La réponse en cas de succès sera :

        {
            "message": "Vos informations ont été mises à jour avec succès."
        }

    Raises:
        ValidationError: Si les données fournies ne respectent pas le schéma défini.
        Exception: Pour toutes les autres erreurs survenant lors de la mise à jour des informations.
    """
    try:
        user = get_current_user()

        if not user:
            return (
                jsonify({"message": "Aucun utilisateur trouvé", "errors": True}),
                404,
            )

        data = request.get_json()
        userUpdateInfoSchema = UserUpdateSchema()
        user_data = userUpdateInfoSchema.load(data)

        if "first_name" in user_data:
            user.first_name = user_data["first_name"]
        if "last_name" in user_data:
            user.last_name = user_data["last_name"]
        if "email" in user_data:
            user.email = user_data["email"]
        if "notification" in user_data:
            user.notification = user_data["notification"]

        db.session.commit()

        return (
            jsonify({"message": "Vos informations ont été mises à jour avec succès."}),
            200,
        )
    except ValidationError as err:
        return (
            jsonify(
                {
                    "errors": True,
                    "message": "Erreur de mise à jours des informations",
                    "details": err.messages,
                }
            ),
            400,
        )
    except Exception as e:
        return (
            jsonify(
                {
                    "errors": True,
                    "message": "Une erreur est survenue",
                    "details": str(e),
                }
            ),
            500,
        )


@user_bp.route("/update-password", methods=["PUT"])
@jwt_required()
def update_password():
    """
    Met à jour le mot de passe de l'utilisateur connecté.

    Cette fonction permet à un utilisateur de changer son mot de passe.
    L'utilisateur doit fournir son ancien mot de passe ainsi qu'un nouveau
    mot de passe. La validation s'assure que le nouveau mot de passe est
    différent de l'ancien et que l'ancien mot de passe est correct.

    Returns:
        Response:
            - 200 OK: Si le mot de passe a été mis à jour avec succès.
            - 404 Not Found: Si aucun utilisateur n'est trouvé pour l'identité fournie.
            - 400 Bad Request: En cas d'ancien mot de passe incorrect,
              ou si le nouveau mot de passe est identique à l'ancien.
            - 400 Bad Request: En cas d'erreur de validation lors de la mise à jour du mot de passe.
            - 500 Internal Server Error: Pour toute autre erreur survenant lors du traitement.

    Example:
        Pour utiliser cette fonction, envoyez une requête PUT à l'URL `/update-password`
        avec un token JWT valide dans l'en-tête d'autorisation et des données JSON dans
        le corps de la requête, par exemple :

        {
            "old_password": "AncienMotDePasse",
            "new_password": "NouveauMotDePasse"
        }

        La réponse en cas de succès sera :

        {
            "message": "Votre mot de passe a été mis à jour avec succès."
        }

    Raises:
        ValidationError: Si les données fournies ne respectent pas le schéma défini.
        Exception: Pour toutes les autres erreurs survenant lors de la mise à jour du mot de passe.
    """
    try:
        user = get_current_user()

        if not user:
            return (
                jsonify({"message": "Aucun utilisateur trouvé", "errors": True}),
                404,
            )

        data = request.get_json()
        userUpdatePassword = UserPasswordUpdateSchema()
        user_data = userUpdatePassword.load(data)
        if not pwd_context.verify(user_data["old_password"], user.password_hash):
            return (
                jsonify(
                    {
                        "message": "L'ancien mot de passe est incorrect.",
                        "errors": True,
                        "details": {"password": "L'ancien mot de passe est incorrect."},
                    }
                ),
                400,
            )

        if pwd_context.verify(user_data["new_password"], user.password_hash):
            return (
                jsonify(
                    {
                        "message": "Le nouveau mot de passe doit être différent de l'ancien.",
                        "errors": True,
                        "details": {
                            "new_password": "Le nouveau mot de passe doit être différent de l'ancien."
                        },
                    }
                ),
                400,
            )

        user.password_hash = user_data["new_password"]
        db.session.commit()
        return (
            jsonify({"message": "Votre mot de passe à été mises à jour avec succès."}),
            200,
        )

    except ValidationError as err:
        return (
            jsonify(
                {
                    "errors": True,
                    "message": "Erreur de mise à jour de votre mot de passe",
                    "details": {"new_password": err.messages.get("new_password", [])},
                }
            ),
            400,
        )
    except Exception as e:
        return (
            jsonify(
                {
                    "errors": True,
                    "message": "Une erreur est survenue",
                    "details": str(e),
                }
            ),
            500,
        )


@user_bp.route("/logout", methods=["POST"])
@jwt_required()
def logout_user():
    """
    Déconnecte l'utilisateur actuel.

    Cette fonction permet à un utilisateur de se déconnecter en révoquant
    le token JWT actuel. Cela empêche toute utilisation future de ce token
    pour accéder aux ressources protégées.

    Returns:
        Response:
            - 200 OK: Si la déconnexion a réussi.
            - 500 Internal Server Error: Pour toute erreur survenant lors du traitement.

    Example:
        Pour utiliser cette fonction, envoyez une requête POST à l'URL `/logout`
        avec un token JWT valide dans l'en-tête d'autorisation. La réponse en cas de succès
        sera :

        {
            "message": "Déconnexion réussie."
        }

    Raises:
        Exception: Pour toute erreur survenant lors de la révocation du token.
    """
    try:
        jti = get_jwt()["jti"]
        user_id = get_jwt_identity()
        revoke_token(jti, user_id)
        return jsonify({"message": "Déconnexion réussie."}), 200
    except Exception as e:
        return (
            jsonify(
                {
                    "errors": True,
                    "message": "Une erreur est survenue",
                    "details": str(e),
                }
            ),
            500,
        )


@user_bp.route("/lottery-registry", methods=["POST"])
@jwt_required()
def lottery_registry():
    """
    Enregistre un utilisateur pour participer à une loterie.

    Cette fonction permet à un utilisateur authentifié de s'inscrire à une
    loterie en fournissant ses numéros et numéros chanceux. La loterie
    doit être active et ne doit pas être terminée.

    Returns:
        Response:
            - 201 Created: Si l'inscription à la loterie est réussie.
            - 400 Bad Request: Si la loterie n'est pas active ou si l'enregistrement échoue.
            - 404 Not Found: Si l'utilisateur ou la loterie n'est pas trouvé.
            - 500 Internal Server Error: Pour toute erreur survenant lors du traitement.

    Example:
        Pour utiliser cette fonction, envoyez une requête POST à l'URL `/lottery-registry`
        avec un token JWT valide dans l'en-tête d'autorisation et un corps JSON comme suit :

        {
            "lottery_id": 1,
            "numbers": [1, 2, 3, 4, 5],
            "lucky_numbers": [6, 7]
        }

        La réponse en cas de succès sera :

        {
            "message": "Inscription à la loterie réussie."
        }

    Raises:
        ValidationError: Pour toute erreur lors de la validation des données d'entrée.
        Exception: Pour toute erreur survenant lors de l'enregistrement à la loterie.
    """
    try:
        user_id = get_jwt_identity()
        if not user_id:
            return (
                jsonify({"message": "Aucun utilisateur trouvé", "errors": True}),
                404,
            )

        data = request.get_json()
        entryRegistrySchema = EntryRegistrySchema()
        entryResgistryData = entryRegistrySchema.load(data)

        lottery = Lottery.query.get(entryResgistryData["lottery_id"])
        if not lottery:
            return (
                jsonify({"message": "Loterie non trouvée.", "errors": True}),
                404,
            )

        if lottery.status in [Status.TERMINE.value] or lottery.is_active:
            return (
                jsonify(
                    {
                        "message": "La loterie n'est pas active ou n'est pas en cours.",
                        "errors": True,
                    }
                ),
                400,
            )

        new_entry = Entry(
            user_id=user_id,
            lottery_id=entryResgistryData["lottery_id"],
            numbers=entryResgistryData["numbers"],
            lucky_numbers=entryResgistryData["lucky_numbers"],
        )

        db.session.add(new_entry)
        db.session.commit()

        return (
            jsonify(
                {
                    "message": "Inscription à la loterie réussie.",
                }
            ),
            201,
        )

    except ValidationError as err:
        return (
            jsonify(
                {
                    "errors": True,
                    "message": "Erreur d'enregistrement",
                    "details": err.messages,
                }
            ),
            400,
        )
    except Exception as e:
        return (
            jsonify(
                {
                    "errors": True,
                    "message": "Une erreur est survenue",
                    "details": str(e),
                }
            ),
            500,
        )


@user_bp.route("/lottery/results/<int:lottery_id>", methods=["GET"])
@jwt_required()
def get_lottery_results(lottery_id):
    """
    Récupère les résultats d'une loterie spécifique.

    Cette fonction permet aux utilisateurs authentifiés de consulter les résultats
    d'une loterie en fournissant l'identifiant de la loterie. Les résultats incluent
    les numéros gagnants et les numéros chanceux associés à la loterie.

    Args:
        lottery_id (int): L'identifiant de la loterie dont on souhaite obtenir les résultats.

    Returns:
        Response:
            - 200 OK: Si les résultats de la loterie sont trouvés, renvoie les détails de la loterie.
            - 404 Not Found: Si la loterie ou ses résultats ne sont pas trouvés.
            - 500 Internal Server Error: Pour toute erreur survenant lors du traitement.

    Example:
        Pour utiliser cette fonction, envoyez une requête GET à l'URL
        `/lottery/results/1` (où `1` est l'identifiant de la loterie).
        La réponse en cas de succès sera :

        {
            "lottery_name": "Nom de la loterie",
            "winning_numbers": [1, 2, 3, 4, 5],
            "lucky_numbers": [6, 7]
        }

    Raises:
        Exception: Pour toute erreur survenant lors de la récupération des résultats.
    """
    try:
        lottery = Lottery.query.filter_by(id=lottery_id).one_or_none()

        if not lottery:
            return (
                jsonify({"errors": True, "message": "Tirage non trouvé."}),
                404,
            )

        lottery_result = LotteryResult.query.filter_by(
            lottery_id=lottery_id
        ).one_or_none()

        if not lottery_result:
            return (
                jsonify(
                    {
                        "errors": True,
                        "message": "Aucun résultat trouvé pour ce tirage.",
                    }
                ),
                404,
            )

        return (
            jsonify(
                {
                    "lottery_name": lottery.name,
                    "winning_numbers": lottery_result.winning_numbers,
                    "lucky_numbers": lottery_result.winning_lucky_numbers,
                }
            ),
            200,
        )

    except Exception as e:
        return (
            jsonify(
                {
                    "errors": True,
                    "message": "Une erreur est survenue lors de la récupération des résultats du tirage.",
                    "details": str(e),
                }
            ),
            500,
        )


@user_bp.route("/lottery-history", methods=["GET"])
@jwt_required()
def lottery_history_user():
    """
    Récupère l'historique des participations de l'utilisateur à la loterie.

    Cette fonction permet aux utilisateurs authentifiés de consulter l'historique
    de leurs participations aux loteries, y compris les détails des loteries et
    des participations associées.

    Returns:
        Response:
            - 200 OK: Si l'historique des participations est récupéré avec succès.
            - 400 Bad Request: Si aucune participation n'est trouvée pour l'utilisateur.
            - 404 Not Found: Si l'utilisateur n'est pas trouvé.
            - 500 Internal Server Error: Pour toute erreur survenant lors du traitement.

    Example:
        Pour utiliser cette fonction, envoyez une requête GET à l'URL
        `/lottery-history`. La réponse en cas de succès sera :

        {
            "message": "Historique des participations récupéré avec succès.",
            "data": [
                {
                    "id": 1,
                    "name": "Loterie de Noël",
                    "date": "01 Décembre 2023",
                    "statut": "EN_VALIDATION",
                    "numerosJoues": [1, 2, 3, 4, 5],
                    "numerosChance": [6, 7],
                    "dateTirage": "25 Décembre 2023"
                },
                ...
            ]
        }

    Raises:
        ValidationError: Pour toute erreur survenant lors de la validation des données.
        Exception: Pour toute erreur survenant lors de la récupération de l'historique.
    """
    try:
        user_id = get_jwt_identity()
        if not user_id:
            return (
                jsonify({"message": "Aucun utilisateur trouvé", "errors": True}),
                404,
            )

        user_entries = Entry.query.filter_by(user_id=user_id).all()
        if not user_entries:
            return (
                jsonify(
                    {
                        "message": "Aucune participation trouvée pour cet utilisateur.",
                        "errors": True,
                        "emptyEntries": True,
                    }
                ),
                400,
            )

        lotteries = []
        current_date = datetime.utcnow()

        for entry in user_entries:
            lottery = Lottery.query.get(entry.lottery_id)

            if current_date >= lottery.end_date and lottery.status not in [
                Status.TERMINE.value,
                Status.EN_VALIDATION.value,
            ]:
                lottery.status = Status.EN_VALIDATION.value
                db.session.commit()

            date_participation = lottery.start_date.strftime("%d %B %Y")
            date_tirage = lottery.end_date.strftime("%d %B %Y")

            lotteries.append(
                {
                    "id": lottery.id,
                    "name": lottery.name,
                    "date": date_participation,
                    "statut": lottery.status,
                    "numerosJoues": entry.numbers,
                    "numerosChance": entry.lucky_numbers,
                    "dateTirage": date_tirage,
                }
            )

        schema = LotteryHistorySchema(many=True)
        result = schema.dump(lotteries)

        return (
            jsonify(
                {
                    "message": "Historique des participations récupéré avec succès.",
                    "data": result,
                }
            ),
            200,
        )

    except ValidationError as err:
        return (
            jsonify(
                {
                    "errors": True,
                    "message": "Erreur de récupération de l'historique",
                    "details": err.messages,
                }
            ),
            400,
        )

    except Exception as e:
        return (
            jsonify(
                {
                    "errors": True,
                    "message": "Une erreur est survenue",
                    "details": str(e),
                }
            ),
            500,
        )


@user_bp.route("/lottery/current", methods=["GET"])
@jwt_required()
def get_current_lottery():
    """
    Récupère les informations sur la loterie en cours.

    Cette fonction permet à un utilisateur authentifié de récupérer
    les détails de la loterie actuelle. Elle vérifie également si l'utilisateur
    est déjà inscrit à cette loterie.

    Returns:
        Response:
            - 200 OK: Si la loterie en cours est récupérée avec succès.
            - 400 Bad Request: Si aucune loterie en cours n'est trouvée ou si
              l'utilisateur est déjà inscrit à cette loterie.
            - 404 Not Found: Si l'utilisateur n'est pas trouvé.
            - 500 Internal Server Error: Pour toute erreur survenant lors du traitement.

    Example:
        Pour utiliser cette fonction, envoyez une requête GET à l'URL
        `/lottery/current`. La réponse en cas de succès sera :

        {
            "id": 1,
            "name": "Loterie de Noël",
            "status": "EN_COUR",
            "start_date": "01 Décembre 2023",
            "end_date": "25 Décembre 2023"
        }

    Raises:
        Exception: Pour toute erreur survenant lors de la récupération de la loterie.
    """
    try:
        user = get_current_user()
        if not user:
            return (
                jsonify({"message": "Aucun utilisateur trouvé", "errors": True}),
                404,
            )

        current_lottery = Lottery.query.filter_by(
            _status=Status.EN_COUR.value
        ).one_or_none()

        if not current_lottery:
            return (
                jsonify(
                    {
                        "errors": False,
                        "message": "Aucun tirage en cours trouvé.",
                    }
                ),
                400,
            )
        is_registered = Entry.query.filter_by(
            user_id=user.id, lottery_id=current_lottery.id
        ).one_or_none()
        if is_registered:
            return (
                jsonify(
                    {
                        "errors": True,
                        "message": "Vous êtes déjà inscrit à cette loterie.",
                    }
                ),
                400,
            )

        lottery_schema = LotteryOverviewSchema()
        result = lottery_schema.dump(current_lottery)

        return jsonify(result), 200

    except Exception as e:
        return (
            jsonify(
                {
                    "errors": True,
                    "message": "Une erreur est survenue",
                    "details": str(e),
                }
            ),
            500,
        )


@user_bp.route("/lottery-details/<int:lottery_id>", methods=["GET"])
@jwt_required()
def lottery_details(lottery_id):
    """
    Récupère les détails d'une loterie spécifique.

    Cette fonction permet à un utilisateur authentifié de récupérer
    les détails d'une loterie donnée par son identifiant. Elle vérifie
    également si la loterie a atteint sa date de fin et met à jour son
    statut en conséquence. Les numéros gagnants et les numéros chanceux
    sont également retournés si disponibles.

    Args:
        lottery_id (int): L'identifiant de la loterie dont on souhaite obtenir les détails.

    Returns:
        Response:
            - 200 OK: Si les détails de la loterie sont récupérés avec succès.
            - 400 Bad Request: Si une erreur se produit lors de la récupération.
            - 404 Not Found: Si la loterie avec l'identifiant fourni n'est pas trouvée.
            - 500 Internal Server Error: Pour toute erreur survenant lors du traitement.

    Example:
        Pour utiliser cette fonction, envoyez une requête GET à l'URL
        `/lottery-details/1`. La réponse en cas de succès sera :

        {
            "message": "Details du tirage",
            "data": {
                "id": 1,
                "name": "Loterie de Noël",
                "status": "EN_COUR",
                "start_date": "01 Décembre 2023",
                "end_date": "25 Décembre 2023"
            },
            "numbers": {
                "winning_numbers": "1, 2, 3, 4, 5",
                "lucky_numbers": "6, 7"
            }
        }

    Raises:
        Exception: Pour toute erreur survenant lors de la récupération des détails de la loterie.
    """
    try:
        lottery = Lottery.query.filter_by(id=lottery_id).one_or_none()
        if lottery is None:
            return (
                jsonify({"errors": True, "message": "Loterie non trouvée."}),
                404,
            )

        current_date = datetime.utcnow()
        if current_date >= lottery.end_date and lottery.status not in [
            Status.TERMINE.value,
            Status.EN_VALIDATION.value,
        ]:
            lottery.status = Status.EN_VALIDATION.value
            db.session.commit()
        lotteryOverviewschema = LotteryOverviewSchema()
        result = lotteryOverviewschema.dump(lottery)
        lottery_result = LotteryResult.query.filter_by(
            lottery_id=lottery_id
        ).one_or_none()
        winning_numbers = ""
        lucky_numbers = ""
        if lottery_result:
            winning_numbers = lottery_result.winning_numbers
            lucky_numbers = lottery_result.winning_lucky_numbers
        return (
            jsonify(
                {
                    "message": "Details du tirage",
                    "data": result,
                    "numbers": {
                        "winning_numbers": winning_numbers,
                        "lucky_numbers": lucky_numbers,
                    },
                }
            ),
            200,
        )

    except ValidationError as err:
        return (
            jsonify(
                {
                    "errors": True,
                    "message": "Erreur de récupération de l'historique",
                    "details": err.messages,
                }
            ),
            400,
        )
    except Exception as e:
        return (
            jsonify(
                {
                    "errors": True,
                    "message": "Une erreur est survenue",
                    "details": str(e),
                }
            ),
            500,
        )


@user_bp.route("/lottery-rank/<int:lottery_id>", methods=["GET"])
@jwt_required()
def lottery_rank(lottery_id):
    """
    Récupère le classement des participants d'un tirage de loterie spécifique.

    Cette fonction permet à un utilisateur authentifié d'obtenir le classement
    des participants pour une loterie donnée par son identifiant. Elle renvoie
    également les résultats de l'utilisateur courant s'il a participé à la loterie.

    Args:
        lottery_id (int): L'identifiant du tirage de loterie dont on souhaite obtenir le classement.

    Returns:
        Response:
            - 200 OK: Si le classement des participants est récupéré avec succès.
            - 404 Not Found: Si la loterie ou le classement n'est pas trouvé.
            - 500 Internal Server Error: Pour toute erreur survenant lors du traitement.

    Example:
        Pour utiliser cette fonction, envoyez une requête GET à l'URL
        `/lottery-rank/1`. La réponse en cas de succès sera :

        {
            "message": "Rankings retrieved successfully",
            "data": [
                {
                    "name": "John Doe",
                    "rank": 1,
                    "score": 100,
                    "winnings": 1000
                },
                {
                    "name": "Jane Smith",
                    "rank": 2,
                    "score": 90,
                    "winnings": 500
                }
            ],
            "currentUser": {
                "name": "John Doe",
                "rank": 1,
                "score": 100,
                "winnings": 1000
            }
        }

    Raises:
        Exception: Pour toute erreur survenant lors de la récupération des classements.
    """
    try:
        lottery = Lottery.query.filter_by(id=lottery_id).one_or_none()

        if not lottery:
            return (
                jsonify({"errors": True, "message": "Lottery draw not found."}),
                404,
            )

        lottery_result = (
            db.session.query(LotteryResult)
            .filter_by(lottery_id=lottery_id)
            .one_or_none()
        )
        if lottery_result is None:
            return jsonify({"message": "Aucun résultat pour se tirage"})

        rankings = (
            db.session.query(LotteryRanking)
            .filter_by(lottery_result_id=lottery_result.id)
            .all()
        )

        if not rankings:
            return (
                jsonify(
                    {
                        "message": "No rankings found for this draw.",
                        "errors": True,
                    }
                ),
                404,
            )
        schema = LotteryWinerSchema(many=True)
        schemaCurrentUser = LotteryWinerSchema()
        results = []

        current_user_id = get_jwt_identity()

        results = []
        user_result = None
        validated_user_results = {}

        for ranking in rankings:
            user = db.session.query(User).filter_by(id=ranking.player_id).one_or_none()
            name = user.full_name if user else "Unknown"

            result_data = {
                "name": name,
                "rank": ranking.rank,
                "score": ranking.score,
                "winnings": ranking.winnings,
            }

            results.append(result_data)

            if ranking.player_id == current_user_id:
                user_result = result_data

        validated_results = schema.dump(results)
        if user_result is not None:
            validated_user_results = schemaCurrentUser.dump(user_result)
        return jsonify(
            {
                "message": "Rankings retrieved successfully",
                "data": validated_results,
                "currentUser": validated_user_results,
            }
        )

    except Exception as e:
        return (
            jsonify(
                {
                    "errors": True,
                    "message": "An error occurred during the draw validation.",
                    "details": str(e),
                }
            ),
            500,
        )
