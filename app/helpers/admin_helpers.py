from functools import wraps
from flask_jwt_extended import get_jwt_identity
from flask import jsonify
from app.models import User, Role
from app.tools.roles_tools import Roles
from app.tools import email_sender


def admin_role_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if not user or not user.is_admin:
            return (
                jsonify(
                    {
                        "errors": True,
                        "message": "Accès refusé. L'utilisateur doit être un administrateur.",
                    }
                ),
                403,
            )

        return func(*args, **kwargs)

    return wrapper


def send_email_to_users():
    try:
        users = (
            User.query.join(Role)
            .filter(Role.role_name == Roles.USER, User.notification)
            .all()
        )
        if not users:
            raise Exception("Aucun utilisateur trouver")
        for user in users:
            email_sender(user.email)
    except Exception as e:
        raise Exception(
            "Une erreur est survenue lors de l'envoie des mails"
        )
