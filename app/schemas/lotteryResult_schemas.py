from marshmallow import Schema, fields


class LotteryResultOverviewSchema(Schema):
    """
    Schéma de validation et de sérialisation pour la vue d'ensemble des résultats d'une loterie.

    Ce schéma est utilisé pour formater et valider les données des résultats d'une loterie,
    en incluant les informations liées à la loterie elle-même, telles que le nom, les dates,
    ainsi que les numéros gagnants.

    Attributs:
        name (str): Le nom de la loterie, dérivé de l'attribut "lottery.name".
        start_date (datetime): La date de début de la loterie, dérivée de l'attribut "lottery.start_date".
        end_date (datetime): La date de fin de la loterie, dérivée de l'attribut "lottery.end_date".
        wining_numbers (str): Les numéros gagnants de la loterie.
        wining_lucky_numes (str): Les numéros chanceux gagnants de la loterie.

    Meta:
        - Les attributs "name", "start_date", et "end_date" sont mappés à des champs associés à l'objet "lottery".
        - Les champs "wining_numbers" et "wining_lucky_numes" sont directement associés aux résultats de la loterie.

    Exceptions:
        - ValidationError: Levée en cas de non-respect des règles de validation sur les types de données ou les formats.
    """

    name = fields.Str(attribute="lottery.name")
    start_date = fields.DateTime(attribute="lottery.start_date")
    end_date = fields.DateTime(attribute="lottery.end_date")
    wining_numbers = fields.Str()
    wining_lucky_numes = fields.Str()


class LotteryWinerSchema(Schema):
    """
    Schéma de validation pour les informations relatives aux gagnants d'une loterie.

    Ce schéma est utilisé pour valider et formater les données concernant les gagnants
    d'une loterie, telles que leur identifiant, leur classement, leur nom, leur score,
    et leurs gains.

    Attributs:
        player_id (int): L'identifiant unique du joueur gagnant. Ce champ est requis.
        rank (int): Le rang du joueur dans le classement des gagnants. Ce champ est requis.
        name (str): Le nom complet du joueur. Ce champ est requis.
        score (int): Le score du joueur dans le tirage. Ce champ est requis.
        winnings (float): Le montant des gains du joueur. Ce champ est requis.

    Meta:
        fields (tuple): Les champs inclus dans la sérialisation et la validation des données,
        à savoir "player_id", "rank", "name", "score", et "winnings".

    Exceptions:
        - ValidationError: Levée lorsque les champs ne respectent pas les règles de validation.
    """

    player_id = fields.Int(required=True)
    rank = fields.Int(required=True)
    name = fields.Str(required=True)
    score = fields.Int(required=True)
    winnings = fields.Float(required=True)

    class Meta:
        fields = ("player_id", "rank", "name", "score", "winnings")
