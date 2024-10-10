from marshmallow import Schema, fields, validate, ValidationError


class ContactUsSchema(Schema):
    """
    Schéma de validation pour les demandes de contact.

    Cette classe utilise Marshmallow pour valider les données soumises
    via le formulaire de contact. Elle assure que les données respectent
    les contraintes définies avant d'être traitées.

    Attributes:
        email (str): Adresse email de l'utilisateur. Elle doit être au format
                     email et est requise.
        message (str): Message de l'utilisateur. Il doit contenir au moins
                       1 caractère et au maximum 1000 caractères.

    Example:
        schema = ContactUsSchema()
        result = schema.load({
            "email": "john.doe@example.com",
            "message": "J'aimerais en savoir plus sur vos services."
        })
        # result contiendra un dictionnaire avec les données validées.

        # Pour valider et gérer les erreurs:
        try:
            schema.load({
                "email": "invalid_email",
                "message": ""
            })
        except ValidationError as err:
            print(err.messages)  # Affiche les erreurs de validation
    """

    email = fields.Email(required=True, validate=validate.Length(max=255))
    message = fields.Str(required=True, validate=validate.Length(min=1, max=1000))
