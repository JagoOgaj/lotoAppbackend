from functools import wraps
from flask_jwt_extended import get_jwt_identity
from flask import jsonify
from app.models import User, Role
from app.tools.roles_tools import Roles
from app.tools import email_sender_new_tirage


def admin_role_required(func):
    """
    Décorateur qui exige que l'utilisateur soit un administrateur pour accéder à une fonction.

    Ce décorateur vérifie si l'utilisateur authentifié possède des droits d'administrateur
    avant de lui permettre d'exécuter la fonction décorée. Si l'utilisateur n'est pas
    authentifié ou n'a pas le rôle d'administrateur, un message d'erreur est renvoyé
    avec le statut 403 (Forbidden).

    Args:
        func (Callable): La fonction à décorer qui nécessite des droits d'administrateur.

    Returns:
        Callable: La fonction décorée qui inclut la vérification des droits d'administrateur.

    Raises:
        Exception: Si une erreur se produit lors de la vérification de l'utilisateur.

    Example:
        @app.route("/admin/dashboard")
        @admin_role_required
        def admin_dashboard():
            return jsonify({"message": "Bienvenue sur le tableau de bord de l'administrateur."})
    """

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
    """
    Envoie des emails aux utilisateurs ayant activé les notifications.

    Cette fonction récupère tous les utilisateurs ayant le rôle d'utilisateur (USER)
    et qui ont activé les notifications. Pour chaque utilisateur, un email est envoyé
    via la fonction `email_sender_new_tirage`.

    Raises:
        Exception: Si une erreur se produit lors de la récupération des utilisateurs
        ou de l'envoi des emails, une exception est levée avec un message d'erreur.

    Returns:
        None: La fonction ne retourne rien. Si aucun utilisateur n'est trouvé,
        aucun email n'est envoyé.

    Example:
        send_email_to_users()
    """
    try:
        users = (
            User.query.join(Role)
            .filter(Role.role_name == Roles.USER.value, User.notification)
            .all()
        )
        if not users:
            return
        for user in users:
            email_sender_new_tirage(user.email)
    except Exception as e:
        raise Exception(f"Une erreur est survenue lors de l'envoie des mails {str(e)}")
