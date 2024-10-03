from marshmallow import Schema, fields


class LotteryRankingSchema(Schema):
    id = fields.Int(dump_only=True)  # Only to be returned in responses
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
