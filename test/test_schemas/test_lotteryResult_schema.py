import unittest
from marshmallow import ValidationError
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
from app.schemas import LotteryResultOverviewSchema, LotteryWinerSchema


class TestLotterySchemas(unittest.TestCase):
    def setUp(self):
        self.lottery_result_overview_schema = LotteryResultOverviewSchema()
        self.lottery_winer_schema = LotteryWinerSchema()

    def test_lottery_winer_schema_valid(self):
        valid_data = {
            "player_id": 1,
            "rank": 1,
            "name": "Alice Winner",
            "score": 100,
            "winnings": 10000.0,
        }
        result = self.lottery_winer_schema.load(valid_data)
        self.assertEqual(result["player_id"], valid_data["player_id"])
        self.assertEqual(result["rank"], valid_data["rank"])
        self.assertEqual(result["name"], valid_data["name"])
        self.assertEqual(result["score"], valid_data["score"])
        self.assertEqual(result["winnings"], valid_data["winnings"])

    def test_lottery_winer_schema_invalid_player_id(self):
        invalid_data = {
            "player_id": "invalid_id",  # ID invalide
            "rank": 1,
            "name": "Alice Winner",
            "score": 100,
            "winnings": 10000.0,
        }
        with self.assertRaises(ValidationError) as context:
            self.lottery_winer_schema.load(invalid_data)
        self.assertIn("Not a valid integer.", str(context.exception))

    def test_lottery_winer_schema_missing_required_fields(self):
        invalid_data = {
            "rank": 1,
            "name": "Alice Winner",
            # 'player_id', 'score', et 'winnings' manquent
        }
        with self.assertRaises(ValidationError) as context:
            self.lottery_winer_schema.load(invalid_data)
        self.assertIn("Missing data for required field.", str(context.exception))


if __name__ == "__main__":
    unittest.main()
