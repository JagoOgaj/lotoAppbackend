from flask import request, Blueprint, jsonify
from app.schemas import ContactUsSchema
from marshmallow import ValidationError
from app.tools import email_sender_contact_us

contact_bp = Blueprint("contact", __name__)


@contact_bp.route("/contact-us", methods=["POST"])
def contact_us():
    try:
        data = request.get_json()
        schema = ContactUsSchema()
        data = schema.load(data)
        email_sender_contact_us(data["email"], data["message"])
        return jsonify({"message": "Merci pour votre message"})
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
