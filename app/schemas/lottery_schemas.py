from marshmallow import Schema, fields, post_load, validates, validates_schema, ValidationError
from datetime import datetime
from app.models import Lottery
from app.tools import Status


class LotteryCreateSchema(Schema):
    name = fields.Str(required=True)
    start_date = fields.DateTime(required=True)
    end_date = fields.DateTime(required=True)
    status = fields.Str(required=True)
    max_participants = fields.Int(required=True)

    @validates('name')
    def validate_name(self, value):
        if not value:
            raise ValidationError("Le nom du tirage est requis")

    @validates('status')
    def validate_status(self, value):
        if value not in Status:
            raise ValidationError("Mauvais statut du tirage")

    @validates('max_participants')
    def validate_max_participants(self, value):
        if not value:
            raise ValidationError("Le nombre max de participants est requis")
        if not isinstance(value, int):
            raise ValidationError(
                "Le nombre max de participants doit etre un nombre")

    @validates_schema
    def validate_date(self, data, **kwargs):
        if (not isinstance(data['start_date'], datetime)) or (not isinstance(data['end_date'], datetime)):
            raise ValidationError("Mauvais format pour les dates")
        if data['start_date'] >= data['end_date']:
            raise ValidationError(
                "La fin du tirage ne dois pas etre avant le début du tirage")

    @post_load
    def makeLottery(self, data, **kwargs):
        return Lottery(
            name=data['name'],
            start_date=data['start_date'],
            end_date=data['end_date'],
            status=data['status'],
            max_participants=data['max_participants']
        )

    class Meta:
        fields = ('name', 'start_date', 'end_date',
                  'status', 'max_participants')


class LotteryUpdateSchema(Schema):
    name = fields.Str()
    start_date = fields.DateTime()
    end_date = fields.DateTime()
    status = fields.Str()
    max_participants = fields.Int()

    @validates('name')
    def validate_name(self, value):
        if not value:
            raise ValidationError("Le nom du tirage est requis")

    @validates('status')
    def validate_status(self, value):
        if value not in Status:
            raise ValidationError("Mauvais statut du tirage")

    @validates('max_participants')
    def validate_max_participants(self, value):
        if not value:
            raise ValidationError("Le nombre max de participants est requis")
        if not isinstance(value, int):
            raise ValidationError(
                "Le nombre max de participants doit etre un nombre")

    @validates_schema
    def validate_date(self, data, **kwargs):
        if (not isinstance(data['start_date'], datetime)) or (not isinstance(data['end_date'], datetime)):
            raise ValidationError("Mauvais format pour les dates")
        if data['start_date'] >= data['end_date']:
            raise ValidationError(
                "La fin du tirage ne dois pas etre avant le début du tirage")

    class Meta:
        fileds = ('name', 'start_date', 'end_date',
                  'status', 'max_participants')


class LotteryListSchema(Schema):
    id = fields.Int()
    name = fields.Str()
    start_date = fields.DateTime()
    end_date = fields.DateTime()
    status = fields.Str()
    max_participants = fields.Int()
    participant_count = fields.Int()

    class Meta:
        fields = ('id', 'name', 'start_date', 'end_date', 'status',
                  'participant_count', 'max_participants')


class UserLotteryListSchema(Schema):
    lottery_id = fields.Int(required=True)
    lottery_name = fields.Str(required=True)
    start_date = fields.DateTime(required=True)
    end_date = fields.DateTime(required=True)
    participant_count = fields.Int(required=True)
    max_participants = fields.Int(required=True)
    status = fields.Str(required=True)

    class Meta:
        fields = ('lottery_id', 'lottery_name', 'start_date', 'end_date',
                  'participant_count', 'max_participants', 'status')
