from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token, get_jwt
from app.models import User
from app.helpers import revoke_token, add_token_to_database, is_token_revoked
from app.extensions import jwt, db
from flask import current_app as app


auth_bp = Blueprint('auth', __name__)


@auth_bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    user_id = get_jwt_identity()
    access_token = create_access_token(identity=user_id)
    add_token_to_database(access_token)
    return jsonify({"access_token": access_token}), 201


@auth_bp.route("/revoke_access", methods=["DELETE"])
@jwt_required()
def revoke_access_token():
    jti = get_jwt()["jti"]
    user_id = get_jwt_identity()
    revoke_token(jti, user_id)
    return jsonify({"message": "Token revoked"}), 200


@auth_bp.route("/revoke_refresh", methods=["DELETE"])
@jwt_required(refresh=True)
def revoke_refresh_token():
    jti = get_jwt()["jti"]
    user_id = get_jwt_identity()
    revoke_token(jti, user_id)
    return jsonify({"message": "Refresh token revoked"}), 200


@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_headers, jwt_payload):
    try:
        return is_token_revoked(jwt_payload)
    except Exception:
        return True


@auth_bp.route("/get-role", methods=["GET"])
@jwt_required()
def get_role():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({"message": "User not found"}), 404
    return jsonify({"role": user.role_name}), 200


@jwt.user_lookup_loader
def user_loader_callback(jwt_headers, jwt_payload):
    identity = jwt_payload[app.config["JWT_IDENTITY_CLAIM"]]
    return User.query.get(identity)
