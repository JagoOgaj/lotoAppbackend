from flask import request, Blueprint, jsonify
from app.schemas import ContactUsSchema
from marshmallow import ValidationError
from app.tools import email_sender_contact_us

contact_bp = Blueprint("contact", __name__)


@contact_bp.route("/contact-us", methods=["POST"])
def contact_us():
    """
    Envoie un message de contact à l'administrateur.

    Cette fonction permet aux utilisateurs d'envoyer un message via un formulaire de contact.
    Elle valide les données reçues, envoie un email à l'administrateur avec les informations
    fournies, et renvoie une réponse appropriée.

    Returns:
        Response:
            - Si la demande est réussie, renvoie un message de confirmation.
            - Si une erreur de validation se produit, renvoie un message d'erreur avec les détails.
            - Si une autre exception se produit, renvoie un message d'erreur générique.

    Example:
        Pour utiliser cette fonction, envoyez une requête POST à l'URL `/contact-us`
        avec un corps JSON contenant les champs suivants :

        {
            "email": "user@example.com",
            "message": "Votre message ici."
        }

    Raises:
        ValidationError: Si les données de contact ne respectent pas le schéma défini.
        Exception: Pour toutes les autres erreurs survenant lors de l'envoi de l'email.
    """
    try:
        data = request.get_json()
        schema = ContactUsSchema()
        data = schema.load(data)
        email_sender_contact_us(data["email"], data["message"])
        return jsonify({"message": "Merci pour votre message"}), 200
    except ValidationError as e:
        return (
            jsonify(
                {
                    "message": "Une erreur est survenue lors de l'envoie de votre message",
                    "errors": True,
                    "details": e.messages,
                }
            ),
            404,
        )

    except Exception as e:
        return (
            jsonify(
                {
                    "message": "Une erreur est survenue lors de l'envoie de votre message",
                    "errors": True,
                    "details": str(e),
                }
            ),
            404,
        )
