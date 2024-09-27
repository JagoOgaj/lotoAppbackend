from marshmallow import Schema, ValidationError, fields, post_load, validates, validates_schema
from app.models import User
from app import pwd_context
import re


class UserCreateSchema(Schema):
    first_name = fields.Str(required=True, validate=[
                            fields.Length(min=2, max=50)])
    last_name = fields.Str(required=True, validate=[
                           fields.Length(min=2, max=50)])
    email = fields.Email(required=True)
    password = fields.Str(load_only=True, required=True)

    @validates('email')
    def validate_email(self, value):
        if not value:
            raise ValidationError("L'email est requis.")

        email_regex = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"

        if not re.match(email_regex, value):
            raise ValidationError("Format d'email invalide.")

    @validates('password')
    def validate_password_strength(self, value):
        if len(value) < 8:
            raise ValidationError(
                "Le mot de passe doit contenir au moins 8 caractères.")
        if not any(char.islower() for char in value):
            raise ValidationError(
                "Le mot de passe doit contenir au moins une lettre minuscule.")
        if not any(char.isupper() for char in value):
            raise ValidationError(
                "Le mot de passe doit contenir au moins une lettre majuscule.")
        if not any(char.isdigit() for char in value):
            raise ValidationError(
                "Le mot de passe doit contenir au moins un chiffre.")
        if not any(char in '!@#$%^&*()_+-=[]{}|;:,.<>?/' for char in value):
            raise ValidationError(
                "Le mot de passe doit contenir au moins un caractère spécial.")

    @validates_schema
    def validate_name(self, data, **kwargs):
        if not data['first_name'].strip():
            raise ValidationError(
                "Le prénom ne peut pas être vide ou composé uniquement d'espaces.", field_name="first_name")
        if not data['last_name'].strip():
            raise ValidationError(
                "Le nom ne peut pas être vide ou composé uniquement d'espaces.", field_name="last_name")

    @post_load
    def make_user(self, data, **kwargs):
        return User(
            _first_name=data['first_name'],
            _last_name=data['last_name'],
            _email=data['email'],
            _password_hash=pwd_context.hash(data['password'])
        )

    class Meta:
        fields = ('first_name', 'last_name', 'email', 'password')


class UserUpdateSchema(Schema):
    first_name = fields.Str()
    last_name = fields.Str()
    email = fields.Email()

    @validates('email')
    def validate_email(self, value):
        if not value:
            raise ValidationError("L'email est requis.")

        email_regex = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"

        if not re.match(email_regex, value):
            raise ValidationError("Format d'email invalide.")

    @validates('password')
    def validate_password_strength(self, value):
        if len(value) < 8:
            raise ValidationError(
                "Le mot de passe doit contenir au moins 8 caractères.")
        if not any(char.islower() for char in value):
            raise ValidationError(
                "Le mot de passe doit contenir au moins une lettre minuscule.")
        if not any(char.isupper() for char in value):
            raise ValidationError(
                "Le mot de passe doit contenir au moins une lettre majuscule.")
        if not any(char.isdigit() for char in value):
            raise ValidationError(
                "Le mot de passe doit contenir au moins un chiffre.")
        if not any(char in '!@#$%^&*()_+-=[]{}|;:,.<>?/' for char in value):
            raise ValidationError(
                "Le mot de passe doit contenir au moins un caractère spécial.")

    @validates_schema
    def validate_name(self, data, **kwargs):
        if not data['first_name'].strip():
            raise ValidationError(
                "Le prénom ne peut pas être vide ou composé uniquement d'espaces.", field_name="first_name")
        if not data['last_name'].strip():
            raise ValidationError(
                "Le nom ne peut pas être vide ou composé uniquement d'espaces.", field_name="last_name")

    class Meta:
        fields = ('first_name', 'last_name', 'email')
        exclude = ('password_hash',)


class UserPasswordUpdateSchema(Schema):
    old_password = fields.Str(load_only=True, required=True)
    new_password = fields.Str(load_only=True, required=True)

    @post_load
    def validate_password(self, data, **kwargs):
        user = kwargs.get('user')

        if not pwd_context.verify(data['old_password'], user.password_hash):
            raise ValidationError(
                "L'ancien mot de passe est incorrect.", field_name="old_password")

        if pwd_context.verify(data['new_password'], user.password_hash):
            raise ValidationError(
                "Le nouveau mot de passe doit être différent de l'ancien.", field_name="new_password")

        return data


class UserLoginSchema(Schema):
    email = fields.Str(required=True)
    password = fields.Str(required=True, load_only=True)

    @post_load
    def validate_login(self, data, **kwargs):
        if not data.get('email'):
            raise ValidationError("L'email est requis.")
        if not data.get('password'):
            raise ValidationError("Le mot de passe est requis.")

        return data


class AdminUserOverviewSchema(Schema):
    first_name = fields.Str()
    last_name = fields.Str()
    email = fields.Email()
    role_name = fields.Str(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    update_at = fields.DateTime(dump_only=True)

    class Meta:
        fields = ('first_name', 'last_name', 'email',
                  'role_name', 'created_at', 'update_at')
        dump_only = ('created_at', 'update_at')


class AdminLoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True, load_only=True)

    @post_load
    def validate_admin_login(self, data, **kwargs):
        if not data.get('email'):
            raise ValidationError("L'email est requis.")
        if not data.get('password'):
            raise ValidationError("Le mot de passe est requis.")

        return data
