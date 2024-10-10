from marshmallow import Schema, fields


class LotteryRankingSchema(Schema):
    """
    Schéma de validation pour les classements d'un tirage de loterie.

    Ce schéma est utilisé pour valider et formater les données relatives aux résultats
    des joueurs dans un tirage de loterie, comme leur position dans le classement, leur score,
    et leurs gains.

    Attributs:
        id (int, en lecture seule): L'identifiant unique du classement. Ce champ est en lecture seule.
        lottery_result_id (int): L'identifiant du résultat de la loterie associé à ce classement. Ce champ est requis.
        player_id (int): L'identifiant unique du joueur. Ce champ est requis.
        rank (int): Le rang du joueur dans le classement. Ce champ est requis.
        score (int): Le score du joueur dans le tirage. Ce champ est requis.
        winnings (float): Les gains du joueur en fonction de son classement. Ce champ est requis.

    Meta:
        fields (tuple): Les champs inclus dans la sérialisation et la validation des données.

    Exceptions:
        - ValidationError: Levée lorsque les champs ne respectent pas les règles de validation.
    """

    id = fields.Int(dump_only=True)
    lottery_result_id = fields.Int(required=True)
    player_id = fields.Int(required=True)
    rank = fields.Int(required=True)
    score = fields.Int(required=True)
    winnings = fields.Float(required=True)

    class Meta:
        fields = (
            "id",
            "lottery_result_id",
            "player_id",
            "rank",
            "score",
            "winnings",
        )
