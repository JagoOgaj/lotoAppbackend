from flask_jwt_extended import decode_token
from flask import current_app as app
from datetime import datetime
from app.models import TokenBlockList
from app.extensions import db
from sqlalchemy.exc import NoResultFound


def add_token_to_database(
        encoded_token):
    decoded_token = decode_token(
        encoded_token)

    db_token = TokenBlockList(
        jti=decoded_token['jti'],
        token_type=decoded_token['type'],
        user_id=decoded_token[app.config.get(
            'JWT_IDENTITY_CLAIM')],
        expires=datetime.fromtimestamp(
            decoded_token['exp'])
    )

    db.session.add(db_token)
    db.session.commit()


def revoke_token(token_jti, user_id):
    try:
        token = TokenBlockList.query.filter_by(
            jti=token_jti, user_id=user_id).one()
        token.revoked_at = datetime.utcnow()
        db.session.commit()
    except NoResultFound:
        raise Exception(
            f"Impossible de trouver le token {token_jti}")


def is_token_revoked(jwt_payload):
    jti = jwt_payload['jti']
    user_id = jwt_payload[app.config.get(
        'JWT_IDENTITY_CLAIM')]
    try:
        token = TokenBlockList.query.filter_by(
            jti=jti, user_id=user_id).one()
        return token.revoked_at is not None
    except NoResultFound:
        raise Exception(
            f"Impossible de trouver le token {jti}")
