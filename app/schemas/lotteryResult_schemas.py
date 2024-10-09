from marshmallow import Schema, fields


class LotteryResultOverviewSchema(Schema):
    name = fields.Str(attribute="lottery.name")
    start_date = fields.DateTime(attribute="lottery.start_date")
    end_date = fields.DateTime(attribute="lottery.end_date")
    wining_numbers = fields.Str()
    wining_lucky_numes = fields.Str()


class LotteryWinerSchema(Schema):
    player_id = fields.Int(required=True)
    rank = fields.Int(required=True)
    name = fields.Str(required=True)
    score = fields.Int(required=True)
    winnings = fields.Float(required=True)

    class Meta:
        fields = ("player_id", "rank", "name", "score", "winnings")
