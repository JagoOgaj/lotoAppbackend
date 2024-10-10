from flask_jwt_extended import decode_token
from flask import current_app as app
from datetime import datetime
from app.models import TokenBlockList
from app.extensions import db
from sqlalchemy.exc import NoResultFound


def add_token_to_database(encoded_token):
    """
    Ajoute un jeton JWT à la liste de blocage dans la base de données.

    Cette fonction décode un jeton JWT encodé et enregistre ses informations
    pertinentes dans la table de la base de données `TokenBlockList`, y compris
    le JTI (identifiant unique du jeton), le type de jeton, l'ID de l'utilisateur
    associé et la date d'expiration.

    Args:
        encoded_token (str): Le jeton JWT encodé à ajouter à la liste de blocage.

    Raises:
        Exception: Si une erreur survient lors de la décodification du jeton ou
        de l'ajout à la base de données.

    Example:
        token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
        add_token_to_database(token)

    Note:
        - Assurez-vous que la fonction `decode_token` est définie et fonctionne
        correctement pour extraire les informations du jeton.
        - La table `TokenBlockList` doit être correctement configurée dans
        votre modèle de base de données pour accepter les valeurs fournies.
    """
    decoded_token = decode_token(encoded_token)

    db_token = TokenBlockList(
        jti=decoded_token["jti"],
        token_type=decoded_token["type"],
        user_id=decoded_token[app.config.get("JWT_IDENTITY_CLAIM")],
        expires=datetime.fromtimestamp(decoded_token["exp"]),
    )

    db.session.add(db_token)
    db.session.commit()


def revoke_token(token_jti, user_id):
    """
    Révoque un jeton JWT en le marquant comme révoqué dans la base de données.

    Cette fonction recherche un jeton spécifique dans la table `TokenBlockList`
    en utilisant son JTI (identifiant unique du jeton) et l'ID de l'utilisateur.
    Si le jeton est trouvé, sa date de révocation est mise à jour pour indiquer
    qu'il n'est plus valide.

    Args:
        token_jti (str): L'identifiant unique du jeton (JTI) à révoquer.
        user_id (int): L'identifiant de l'utilisateur dont le jeton doit être révoqué.

    Raises:
        Exception: Si le jeton ne peut pas être trouvé dans la base de données.

    Example:
        revoke_token("jti_example", 123)

    Note:
        - Assurez-vous que la table `TokenBlockList` contient les colonnes `jti`,
        `user_id` et `revoked_at` pour que cette fonction fonctionne correctement.
        - La gestion des exceptions pourrait être améliorée pour inclure des
        vérifications supplémentaires sur la validité du token ou l'utilisateur.
    """
    try:
        token = TokenBlockList.query.filter_by(jti=token_jti, user_id=user_id).one()
        token.revoked_at = datetime.utcnow()
        db.session.commit()
    except NoResultFound:
        raise Exception(f"Impossible de trouver le token {token_jti}")


def is_token_revoked(jwt_payload):
    """
    Vérifie si un jeton JWT a été révoqué en consultant la base de données.

    Cette fonction extrait l'identifiant unique du jeton (JTI) et l'identifiant
    de l'utilisateur à partir de la charge utile du jeton (jwt_payload).
    Elle interroge ensuite la table `TokenBlockList` pour déterminer si
    le jeton est marqué comme révoqué.

    Args:
        jwt_payload (dict): La charge utile du jeton JWT, contenant des
        informations sur l'utilisateur et le jeton.

    Returns:
        bool: True si le jeton a été révoqué, sinon False.

    Raises:
        Exception: Si le jeton ne peut pas être trouvé dans la base de données.

    Example:
        payload = {
            "jti": "token_jti_example",
            "sub": "user_id_example"
        }
        revoked = is_token_revoked(payload)

    Note:
        - Assurez-vous que la table `TokenBlockList` contient les colonnes
        `jti`, `user_id` et `revoked_at` pour que cette fonction fonctionne
        correctement.
        - L'utilisation de cette fonction est essentielle pour vérifier
        l'authenticité des jetons lors des requêtes protégées.
    """
    jti = jwt_payload["jti"]
    user_id = jwt_payload[app.config.get("JWT_IDENTITY_CLAIM")]
    try:
        token = TokenBlockList.query.filter_by(jti=jti, user_id=user_id).one()
        return token.revoked_at is not None
    except NoResultFound:
        raise Exception(f"Impossible de trouver le token {jti}")
