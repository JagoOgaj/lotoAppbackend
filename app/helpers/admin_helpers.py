from functools import wraps
from flask_jwt_extended import get_jwt_identity
from flask import jsonify
from app.models import User


def admin_role_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if not user or not user.is_admin:
            return jsonify({"errors": True, "message": "Accès refusé. L'utilisateur doit être un administrateur."}), 403

        return func(*args, **kwargs)
    return wrapper
