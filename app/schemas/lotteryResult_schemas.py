from marshmallow import Schema, fields


class LotteryResultOverviewSchema(Schema):
    name = fields.Str(attribute='lottery.name')
    start_date = fields.DateTime(attribute='lottery.start_date')
    end_date = fields.DateTime(attribute='lottery.end_date')
    wining_numbers = fields.Str()


class LotteryWinerSchema(Schema):
    rank = fields.Int(required=True)
    name = fields.Str(required=True)
    score = fields.Int(required=True)
    winnings = fields.Int(required=True)

    class Meta:
        fields = ('rank', 'name', 'score', 'winnings')
