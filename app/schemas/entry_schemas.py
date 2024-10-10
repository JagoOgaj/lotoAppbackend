from marshmallow import Schema, fields, validates, ValidationError
import re


class EntryOverviewSchema(Schema):
    """
    Schéma de vue d'ensemble pour les inscriptions à la loterie.

    Cette classe est utilisée pour sérialiser les données des entrées
    des utilisateurs dans une loterie, en fournissant des informations
    telles que l'ID de l'utilisateur, le nom de l'utilisateur, l'email,
    ainsi que les numéros choisis.

    Attributes:
        user_id (int): ID de l'utilisateur qui a effectué l'inscription.
        user_name (str): Nom complet de l'utilisateur (sérialisé à partir de l'objet User).
        email (str): Adresse email de l'utilisateur (sérialisé à partir de l'objet User).
        numbers (str): Numéros choisis par l'utilisateur pour la loterie.
        lucky_numbers (str): Numéros chanceux choisis par l'utilisateur.

    Example:
        schema = EntryOverviewSchema()
        result = schema.dump({
            "user_id": 1,
            "user": {"full_name": "John Doe", "email": "john.doe@example.com"},
            "numbers": "5,12,23,34,45",
            "lucky_numbers": "2,8"
        })
        # result contiendra un dictionnaire avec les données sérialisées.
    """

    user_id = fields.Int()
    user_name = fields.Str(attribute="user.full_name")
    email = fields.Str(attribute="user.email")
    numbers = fields.Str()
    lucky_numbers = fields.Str()

    class Meta:
        fields = (
            "user_id",
            "user_name",
            "email",
            "numbers",
            "lucky_numbers",
        )


class EntryRegistrySchema(Schema):
    """
    Schéma pour l'enregistrement des entrées à la loterie.

    Cette classe est utilisée pour valider les données soumises lors
    de l'inscription d'un utilisateur à une loterie. Elle assure que
    les numéros choisis respectent les règles définies.

    Attributes:
        lottery_id (int): ID de la loterie à laquelle l'utilisateur s'inscrit.
        numbers (str): Numéros classiques choisis par l'utilisateur pour la loterie.
        lucky_numbers (str): Numéros chanceux choisis par l'utilisateur.

    Validations:
        - numbers: Doit contenir au moins 5 numéros uniques entre 1 et 49.
        - lucky_numbers: Doit contenir au maximum 2 numéros uniques entre 1 et 9.

    Example:
        schema = EntryRegistrySchema()
        validated_data = schema.load({
            "lottery_id": 1,
            "numbers": "5,12,23,34,45",
            "lucky_numbers": "2,8"
        })
        # validated_data contiendra les données validées prêtes à être utilisées.

        # Pour gérer les erreurs de validation:
        try:
            schema.load({
                "lottery_id": 1,
                "numbers": "5,12",
                "lucky_numbers": "2,10"
            })
        except ValidationError as err:
            print(err.messages)  # Affiche les erreurs de validation
    """

    lottery_id = fields.Int(required=True)
    numbers = fields.Str(required=True)
    lucky_numbers = fields.Str(required=True)

    @validates("numbers")
    def validate_numbers(self, value):
        if not value:
            raise ValidationError("Les numéros classiques sont requis")

        number_list = [int(num) for num in value.split(",")]

        if len(number_list) < 5:
            raise ValidationError("Il manque des numéros (minimum 5 requis)")

        if len(set(number_list)) != len(number_list):
            raise ValidationError("Les numéros doivent être différents")
        if list(filter(lambda x: not (1 <= x <= 49), number_list)):
            raise ValidationError("Les numéros doivent être entre 1 et 49")

    @validates("lucky_numbers")
    def validate_numbers_lucky(self, value):
        if not value:
            raise ValidationError("Les numéros chanceux sont requis")

        lucky_number_list = [int(num) for num in value.split(",")]

        if len(lucky_number_list) > 2:
            raise ValidationError("Un maximum de 2 numéros chanceux est autorisé")

        if len(set(lucky_number_list)) != len(lucky_number_list):
            raise ValidationError("Les numéros chanceux doivent être différents")

        if list(filter(lambda x: not (1 <= x <= 9), lucky_number_list)):
            raise ValidationError("Les numéros doivent être entre 1 et 9")


class EntryAdminAddUserSchema(Schema):
    """
    Schéma pour l'ajout d'un utilisateur à une loterie par un administrateur.

    Cette classe valide les informations fournies par un administrateur lorsqu'il
    ajoute un utilisateur à une loterie. Elle s'assure que les champs obligatoires
    sont remplis et que les numéros choisis respectent les contraintes définies.

    Attributes:
        user_name (str): Nom complet de l'utilisateur.
        email (str): Adresse email de l'utilisateur.
        numbers (str): Numéros classiques choisis par l'utilisateur.
        numbers_lucky (str): Numéros chanceux choisis par l'utilisateur.

    Validations:
        - user_name: Ne peut pas être vide.
        - email: Doit être valide et suivre un format d'email correct.
        - numbers: Doit contenir au moins 5 numéros uniques entre 1 et 49.
        - numbers_lucky: Doit contenir au maximum 2 numéros uniques entre 1 et 9.

    Example:
        schema = EntryAdminAddUserSchema()
        validated_data = schema.load({
            "user_name": "John Doe",
            "email": "john.doe@example.com",
            "numbers": "5,12,23,34,45",
            "numbers_lucky": "2,8"
        })
        # validated_data contiendra les données validées prêtes à être utilisées.

        # Pour gérer les erreurs de validation:
        try:
            schema.load({
                "user_name": "John Doe",
                "email": "invalid-email",
                "numbers": "5,12",
                "numbers_lucky": "2,10"
            })
        except ValidationError as err:
            print(err.messages)  # Affiche les erreurs de validation
    """

    user_name = fields.Str(attribute="user.full_name")
    email = fields.Str(attribute="user.email")
    numbers = fields.Str()
    numbers_lucky = fields.Str()

    @validates("numbers")
    def validate_numbers(self, value):
        if not value:
            raise ValidationError("Les numéros classiques sont requis")

        number_list = [int(num) for num in value.split(",")]

        if len(number_list) < 5:
            raise ValidationError("Il manque des numéros (minimum 5 requis)")

        if len(set(number_list)) != len(number_list):
            raise ValidationError("Les numéros doivent être différents")
        if list(filter(lambda x: not (1 <= x <= 49), number_list)):
            raise ValidationError("Les numéros doivent être entre 1 et 49")

    @validates("numbers_lucky")
    def validate_numbers_lucky(self, value):
        if not value:
            raise ValidationError("Les numéros chanceux sont requis")

        lucky_number_list = [int(num) for num in value.split(",")]

        if len(lucky_number_list) > 2:
            raise ValidationError("Un maximum de 2 numéros chanceux est autorisé")

        if len(set(lucky_number_list)) != len(lucky_number_list):
            raise ValidationError("Les numéros chanceux doivent être différents")

        if list(filter(lambda x: not (1 <= x <= 10), lucky_number_list)):
            raise ValidationError("Les numéros doivent être entre 1 et 9")

    @validates("email")
    def validate_email(self, value):
        if not value:
            raise ValidationError("L'email est requis et ne peut pas être vide.")
        email_regex = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
        if not re.match(email_regex, value):
            raise ValidationError("Format d'email invalide.")

    @validates("user_name")
    def validate_user_name(self, value):
        if not value:
            raise ValidationError(
                "Le nom de l'utilisateur est requis et ne peut pas être vide."
            )

    class Meta:
        fields = ("user_name", "email", "numbers", "numbers_lucky")
