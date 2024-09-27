from marshmallow import Schema, fields, validates, post_load, ValidationError
from app.models import Entry


class EntryOverviewSchema(Schema):
    user_id = fields.Int()
    user_name = fields.Str(attribute='user.full_name')
    email = fields.Str(attribute='user.email')
    numbers = fields.Str()
    numbers_lucky = fields.Str()

    class Meta:
        fields = ('user_id', 'user_name', 'email', 'numbers_played')


class EntryRegistrySchema(Schema):
    user_id = fields.Int(required=True)
    lottery_id = fields.Int(required=True)
    numbers = fields.Str(required=True)
    numbers_lucky = fields.Str(required=True)

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

    @validates('numbers_lucky')
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

    @post_load
    def make_entry(self, data, **kwargs):
        return Entry(
            user_id=data['user_id'],
            lottery_id=data['lottery_id'],
            numbers=data['numbers'],
            numbers_lucky=data['numbers_lucky']
        )


class EntryRemovalSchema(Schema):
    user_id = fields.Int(required=True)
    lottery_id = fields.Int(required=True)

    @validates('user_id')
    def validate_user_id(self, value):
        if not value:
            raise ValidationError("L'ID de l'utilisateur est requis")

    @validates('lottery_id')
    def validate_lottery_id(self, value):
        if not value:
            raise ValidationError("L'ID du tirage est requis")
