from marshmallow import (
    Schema,
    fields,
    validates,
    ValidationError,
)
from datetime import datetime
from app.tools import Status


class LotteryCreateSchema(Schema):
    """
    Schéma pour la création d'une loterie.

    Ce schéma valide les champs requis lors de la création d'une loterie, tels que
    le nom, les dates, le statut, le prix de la récompense, et le nombre maximum
    de participants. Il inclut des validations spécifiques pour garantir la validité
    des données fournies.

    Attributs:
        name (str): Nom de la loterie. Ce champ est requis.
        start_date (str): Date de début de la loterie. Ce champ est facultatif.
        end_date (str): Date de fin de la loterie. Ce champ est facultatif.
        status (str): Statut de la loterie (ex: actif, terminé). Ce champ est requis.
        reward_price (int): Montant de la récompense à distribuer. Ce champ est requis.
        max_participants (int): Nombre maximum de participants pour la loterie. Ce champ est requis.

    Validations:
        - name: Ne doit pas être vide.
        - status: Doit être un statut valide appartenant à l'énumération `Status`.
        - max_participants: Doit être un nombre entier positif supérieur à 0.
        - reward_price: Doit être un entier supérieur à 0, représentant la récompense à distribuer.

    Exceptions:
        - ValidationError: Levée lorsque les champs ne respectent pas les règles de validation.
    """

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
    """
    Schéma pour la mise à jour d'une loterie.

    Ce schéma permet la validation des champs lors de la mise à jour d'une loterie existante.
    Contrairement à la création, tous les champs sont facultatifs, mais si fournis, ils doivent
    respecter certaines règles de validation.

    Attributs:
        name (str, optionnel): Nom de la loterie. Doit avoir au moins 2 caractères s'il est fourni.
        reward_price (int, optionnel): Montant de la récompense. Doit être un entier positif.
        start_date (str, optionnel): Date de début de la loterie, au format chaîne de caractères.
        end_date (str, optionnel): Date de fin de la loterie, au format chaîne de caractères.
        status (str, optionnel): Statut de la loterie. Doit appartenir à l'énumération `Status` s'il est fourni.
        max_participants (int, optionnel): Nombre maximum de participants. Doit être un entier supérieur à 0 s'il est fourni.

    Validations:
        - name: Si fourni, doit avoir au moins 2 caractères.
        - status: Si fourni, doit être un statut valide appartenant à l'énumération `Status`.
        - max_participants: Si fourni, doit être un entier supérieur à 0.
        - reward_price: Si fourni, doit être un entier positif.

    Exceptions:
        - ValidationError: Levée lorsque les champs ne respectent pas les règles de validation.

    Meta:
        fields: Les champs qui seront inclus dans le schéma (name, start_date, end_date, status, max_participants).
    """

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
    """
    Schéma pour la représentation de l'historique des tirages de loterie.

    Ce schéma est utilisé pour valider et structurer les informations liées à un tirage
    de loterie historique, telles que son identifiant, son nom, sa date, et les numéros joués.

    Attributs:
        id (int): L'identifiant unique du tirage. Doit être fourni et être un entier.
        name (str): Le nom du tirage de loterie. Ce champ est requis.
        date (str): La date associée à l'enregistrement du tirage, généralement la date de création ou de clôture.
        statut (str): Le statut du tirage (par exemple, terminé, en cours, annulé). Ce champ est requis.
        numerosJoues (str): Les numéros classiques joués lors du tirage. Ce champ est requis.
        numerosChance (str): Les numéros chance joués lors du tirage. Ce champ est requis.
        dateTirage (str): La date exacte du tirage. Ce champ est requis.

    Exceptions:
        - ValidationError: Levée lorsque les champs ne respectent pas les règles de validation.

    Remarque:
        - Tous les champs sont obligatoires dans ce schéma.
    """

    id = fields.Int(required=True)
    name = fields.Str(required=True)
    date = fields.Str(required=True)
    statut = fields.Str(required=True)
    numerosJoues = fields.Str(required=True)
    numerosChance = fields.Str(required=True)
    dateTirage = fields.Str(required=True)


class LotteryOverviewSchema(Schema):
    """
    Schéma de validation pour un aperçu de loterie.

    Ce schéma est utilisé pour valider et formater les données relatives à un tirage
    de loterie, telles que l'identifiant du tirage, son nom, ses dates, son statut,
    le montant de la récompense, et le nombre de participants.

    Attributs:
        id (int): L'identifiant unique du tirage de loterie. Ce champ est requis.
        name (str): Le nom du tirage de loterie. Ce champ est requis.
        start_date (DateTime, facultatif): La date de début du tirage. Peut être nulle.
        end_date (DateTime, facultatif): La date de fin du tirage. Peut être nulle.
        status (str): Le statut du tirage (par exemple, actif, terminé). Ce champ est requis.
        reward_price (int): La récompense en jeu pour le tirage. Ce champ est requis.
        max_participants (int): Le nombre maximum de participants autorisés pour ce tirage. Ce champ est requis.
        participant_count (int): Le nombre actuel de participants à ce tirage. Ce champ est requis.

    Meta:
        fields (tuple): Les champs inclus dans la sérialisation et la validation des données.

    Exceptions:
        - ValidationError: Levée lorsque les champs ne respectent pas les règles de validation.
    """

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
