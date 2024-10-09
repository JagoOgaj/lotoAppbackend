from marshmallow import (
    Schema,
    fields,
    validates,
    validates_schema,
    ValidationError,
)
from datetime import datetime
from app.tools import Status


class LotteryCreateSchema(Schema):
    name = fields.Str(required=True)
    start_date = fields.Str(required=False)
    end_date = fields.Str(required=False)
    status = fields.Str(required=True)
    reward_price = fields.Int(required=True)
    max_participants = fields.Int(required=True)

    @validates("name")
    def validate_name(self, value):
        if not value:
            raise ValidationError("Le nom du tirage est requis")

    @validates("status")
    def validate_status(self, value):
        if value not in Status:
            raise ValidationError("Le tirage doit avoir un status")

    @validates("max_participants")
    def validate_max_participants(self, value):
        if not value:
            raise ValidationError("Le nombre max de participants est requis")
        if not isinstance(value, int):
            raise ValidationError("Le nombre max de participants doit etre un nombre")

    @validates("reward_price")
    def validate_reward_price(self, value):
        if not value:
            raise ValidationError("La récompence est requis")
        if not isinstance(value, int):
            raise ValidationError("La récompence doit etre un entier")
        if value <= 0:
            raise ValidationError(
                "La récompence ne doit pas etre superieur ou egal a 0"
            )


class LotteryUpdateSchema(Schema):
    name = fields.Str(required=False)
    reward_price = fields.Int(required=False)
    start_date = fields.Str(required=False)
    end_date = fields.Str(required=False)
    status = fields.Str(required=False)
    max_participants = fields.Int(required=False)

    @validates("name")
    def validate_name(self, value):
        if value:
            if len(value) < 2:
                raise ValidationError("Le nom du tirage doit etre de 2 charectere min")

    @validates("status")
    def validate_status(self, value):
        if value:
            if value not in Status:
                raise ValidationError("Mauvais statut du tirage")

    @validates("max_participants")
    def validate_max_participants(self, value):
        if value:
            if not isinstance(value, int):
                raise ValidationError(
                    "Le nombre max de participants doit etre un nombre"
                )

            if value <= 0:
                raise ValidationError(
                    "Le nombre max de participants doit etre superieur a 0"
                )

    @validates("reward_price")
    def validate_reward_price(self, value):
        if value:
            if not isinstance(value, int):
                raise ValidationError("La recompense doit etre un nombre")
            if value <= 0:
                raise ValidationError("La recompense doit etre superieur a 0")

    class Meta:
        fileds = (
            "name",
            "start_date",
            "end_date",
            "status",
            "max_participants",
        )


class LotteryHistorySchema(Schema):
    id = fields.Int(required=True)
    name = fields.Str(required=True)
    date = fields.Str(required=True)
    statut = fields.Str(required=True)
    numerosJoues = fields.Str(required=True)
    numerosChance = fields.Str(required=True)
    dateTirage = fields.Str(required=True)


class LotteryOverviewSchema(Schema):
    id = fields.Int(required=True)
    name = fields.Str(required=True)
    start_date = fields.DateTime(required=False, allow_none=True)
    end_date = fields.DateTime(required=False, allow_none=True)
    status = fields.Str(required=True)
    reward_price = fields.Int(required=True)
    max_participants = fields.Int(required=True)
    participant_count = fields.Int(required=True)

    class Meta:
        fields = (
            "id",
            "name",
            "start_date",
            "end_date",
            "status",
            "reward_price",
            "participant_count",
            "max_participants",
        )
