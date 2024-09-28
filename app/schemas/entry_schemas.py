from marshmallow import Schema, fields, validates, post_load, ValidationError
import re

class EntryOverviewSchema(Schema):
    user_id = fields.Int()
    user_name = fields.Str(attribute='user.full_name')
    email = fields.Str(attribute='user.email')
    numbers = fields.Str()
    numbers_lucky = fields.Str()

    class Meta:
        fields = ('user_id', 'user_name', 'email', 'numbers', 'numbers_lucky')


class EntryRegistrySchema(Schema):
    lottery_id = fields.Int(required=True)
    numbers = fields.Str(required=True)
    lucky_numbers = fields.Str(required=True)

    @validates('numbers')
    def validate_numbers(self, value):
        if not value:
            raise ValidationError("Les numéros classiques sont requis")

        number_list = [int(num) for num in value.split(',')]

        if len(number_list) < 5:
            raise ValidationError("Il manque des numéros (minimum 5 requis)")

        if len(set(number_list)) != len(number_list):
            raise ValidationError("Les numéros doivent être différents")
        if list(filter(lambda x: not (1 <= x <= 49), number_list)):
            raise ValidationError("Les numéros doivent être entre 1 et 49")

    @validates('lucky_numbers')
    def validate_numbers_lucky(self, value):
        if not value:
            raise ValidationError("Les numéros chanceux sont requis")

        lucky_number_list = [int(num) for num in value.split(',')]

        if len(lucky_number_list) > 2:
            raise ValidationError(
                "Un maximum de 2 numéros chanceux est autorisé")

        if len(set(lucky_number_list)) != len(lucky_number_list):
            raise ValidationError(
                "Les numéros chanceux doivent être différents")

        if list(filter(lambda x: not (1 <= x <= 0), lucky_number_list)):
            raise ValidationError("Les numéros doivent être entre 1 et 9")

        
class EntryAdminAddUserSchema(Schema):
    user_name = fields.Str(attribute='user.full_name')
    email = fields.Str(attribute='user.email')
    numbers = fields.Str()
    numbers_lucky = fields.Str()
    
    @validates('numbers')
    def validate_numbers(self, value):
        if not value:
            raise ValidationError("Les numéros classiques sont requis")

        number_list = [int(num) for num in value.split(',')]

        if len(number_list) < 5:
            raise ValidationError("Il manque des numéros (minimum 5 requis)")

        if len(set(number_list)) != len(number_list):
            raise ValidationError("Les numéros doivent être différents")
        if list(filter(lambda x: not (1 <= x <= 49), number_list)):
            raise ValidationError("Les numéros doivent être entre 1 et 49")

    @validates('lucky_numbers')
    def validate_numbers_lucky(self, value):
        if not value:
            raise ValidationError("Les numéros chanceux sont requis")

        lucky_number_list = [int(num) for num in value.split(',')]

        if len(lucky_number_list) > 2:
            raise ValidationError(
                "Un maximum de 2 numéros chanceux est autorisé")

        if len(set(lucky_number_list)) != len(lucky_number_list):
            raise ValidationError(
                "Les numéros chanceux doivent être différents")

        if list(filter(lambda x: not (1 <= x <= 0), lucky_number_list)):
            raise ValidationError("Les numéros doivent être entre 1 et 9")
    
    @validates('email')
    def validate_email(self, value):
        if not value:
            raise ValidationError("L'email est requis et ne peut pas être vide.")
        email_regex = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
        if not re.match(email_regex, value):
            raise ValidationError("Format d'email invalide.")
        
    @validates('user_name')
    def validate_user_name(self, value):
        if not value:
            raise ValidationError("Le nom de l'utilisateur est requis et ne peut pas être vide.")
    class Meta:
        fields = ('user_name', 'email', 'numbers', 'numbers_lucky')