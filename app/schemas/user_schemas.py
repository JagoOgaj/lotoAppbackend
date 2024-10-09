from marshmallow import (
    Schema,
    ValidationError,
    fields,
    validates,
    validates_schema,
)
import re


class UserCreateSchema(Schema):
    first_name = fields.Str(
        required=True,
        validate=[
            fields.Length(
                min=2,
                max=50,
                error="Le prénom doit contenir entre 2 et 50 caractères.",
            )
        ],
    )
    last_name = fields.Str(
        required=True,
        validate=[
            fields.Length(
                min=2,
                max=50,
                error="Le nom doit contenir entre 2 et 50 caractères.",
            )
        ],
    )
    email = fields.Str(
        required=True, error_messages={"required": "L'email est requis."}
    )
    password = fields.Str(load_only=True, required=True)

    @validates("email")
    def validate_email(self, value):
        if not value:
            raise ValidationError("L'email est requis et ne peut pas être vide.")

        if not re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z]{2,}$", value):
            raise ValidationError("Format d'email invalide.")

    @validates("password")
    def validate_password_strength(self, value):
        if len(value) < 8:
            raise ValidationError(
                "Le mot de passe doit contenir au moins 8 caractères."
            )
        if not any(char.islower() for char in value):
            raise ValidationError(
                "Le mot de passe doit contenir au moins une lettre minuscule."
            )
        if not any(char.isupper() for char in value):
            raise ValidationError(
                "Le mot de passe doit contenir au moins une lettre majuscule."
            )
        if not any(char.isdigit() for char in value):
            raise ValidationError("Le mot de passe doit contenir au moins un chiffre.")
        if not any(char in "!@#$%^&*()_+-=[]{}|;:,.<>?/" for char in value):
            raise ValidationError(
                "Le mot de passe doit contenir au moins un caractère spécial."
            )

    @validates_schema
    def validate_name(self, data, **kwargs):
        if not data["first_name"].strip():
            raise ValidationError(
                "Le prénom ne peut pas être vide ou composé uniquement d'espaces.",
                field_name="first_name",
            )
        if not data["last_name"].strip():
            raise ValidationError(
                "Le nom ne peut pas être vide ou composé uniquement d'espaces.",
                field_name="last_name",
            )

    class Meta:
        fields = ("first_name", "last_name", "email", "password")


class UserUpdateSchema(Schema):
    first_name = fields.Str(required=False)
    last_name = fields.Str(required=False)
    email = fields.Email(required=False)
    notification = fields.Boolean(required=False)

    @validates("email")
    def validate_email(self, value):
        if not value:
            raise ValidationError("L'email est requis.")

        email_regex = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"

        if not re.match(email_regex, value):
            raise ValidationError("Format d'email invalide.")

    @validates("first_name")
    def validate_first_name(self, value):
        if value is not None:  # Vérifie uniquement si la valeur est fournie
            if not value.strip():
                raise ValidationError(
                    "Le prénom ne peut pas être vide ou composé uniquement d'espaces."
                )
            if len(value) < 2:
                raise ValidationError("Le prénom doit avoir 2 character au minimum")

    @validates("last_name")
    def validate_last_name(self, value):
        if value is not None:  # Vérifie uniquement si la valeur est fournie
            if not value.strip():
                raise ValidationError(
                    "Le nom ne peut pas être vide ou composé uniquement d'espaces."
                )
            if len(value) < 2:
                raise ValidationError(
                    "Le nom de famille doit avoir 2 character au minimum"
                )


class UserPasswordUpdateSchema(Schema):
    old_password = fields.Str(load_only=True, required=True)
    new_password = fields.Str(load_only=True, required=True)

    @validates("new_password")
    def validate_password_strength(self, value):
        if len(value) < 8:
            raise ValidationError(
                "Le mot de passe doit contenir au moins 8 caractères."
            )
        if not any(char.islower() for char in value):
            raise ValidationError(
                "Le mot de passe doit contenir au moins une lettre minuscule."
            )
        if not any(char.isupper() for char in value):
            raise ValidationError(
                "Le mot de passe doit contenir au moins une lettre majuscule."
            )
        if not any(char.isdigit() for char in value):
            raise ValidationError("Le mot de passe doit contenir au moins un chiffre.")
        if not any(char in "!@#$%^&*()_+-=[]{}|;:,.<>?/" for char in value):
            raise ValidationError(
                "Le mot de passe doit contenir au moins un caractère spécial."
            )


class UserLoginSchema(Schema):
    email = fields.Str(required=True)
    password = fields.Str(required=True, load_only=True)

    @validates("email")
    def validate_email(self, value):
        if not value:
            raise ValidationError("L'email est requis et ne peut pas être vide.")
        email_regex = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"

        if not re.match(email_regex, value):
            raise ValidationError("Format d'email invalide.")

    @validates("password")
    def validate_password(self, value):
        if not value:
            raise ValidationError(
                "Le mot de passe est requis et ne peut pas être vide."
            )


class UserOverviewInfoSchema(Schema):
    first_name = fields.Str(required=True)
    last_name = fields.Str(required=True)
    email = fields.Email(required=True)
    notification = fields.Boolean(required=True)


class UserOverviewAdvancedSchema(Schema):
    first_name = fields.Str()
    last_name = fields.Str()
    email = fields.Email()
    role_name = fields.Str(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    update_at = fields.DateTime(dump_only=True)

    class Meta:
        fields = (
            "first_name",
            "last_name",
            "email",
            "role_name",
            "created_at",
            "update_at",
        )
        dump_only = ("created_at", "update_at")
