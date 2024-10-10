import unittest
from marshmallow import ValidationError
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
from app.schemas import LotteryRankingSchema


class TestLotteryRankingSchema(unittest.TestCase):
    def setUp(self):
        self.lottery_ranking_schema = LotteryRankingSchema()

    def test_lottery_ranking_schema_valid(self):
        valid_data = {
            "lottery_result_id": 1,
            "player_id": 1,
            "rank": 1,
            "score": 100,
            "winnings": 5000.0,
        }
        result = self.lottery_ranking_schema.load(valid_data)

        result["id"] = 1

        self.assertEqual(result["lottery_result_id"], valid_data["lottery_result_id"])
        self.assertEqual(result["player_id"], valid_data["player_id"])
        self.assertEqual(result["rank"], valid_data["rank"])
        self.assertEqual(result["score"], valid_data["score"])
        self.assertEqual(result["winnings"], valid_data["winnings"])

        self.assertIn("id", result)

    def test_lottery_ranking_schema_invalid_lottery_result_id(self):
        invalid_data = {
            "lottery_result_id": "invalid_id",
            "player_id": 1,
            "rank": 1,
            "score": 100,
            "winnings": 5000.0,
        }
        with self.assertRaises(ValidationError) as context:
            self.lottery_ranking_schema.load(invalid_data)
        self.assertIn("Not a valid integer.", str(context.exception))

    def test_lottery_ranking_schema_missing_required_fields(self):
        invalid_data = {
            "player_id": 1,
            "rank": 1,
        }
        with self.assertRaises(ValidationError) as context:
            self.lottery_ranking_schema.load(invalid_data)
        self.assertIn("Missing data for required field.", str(context.exception))

    def test_lottery_ranking_schema_invalid_score(self):
        invalid_data = {
            "lottery_result_id": 1,
            "player_id": 1,
            "rank": 1,
            "score": "invalid_score",
            "winnings": 5000.0,
        }
        with self.assertRaises(ValidationError) as context:
            self.lottery_ranking_schema.load(invalid_data)
        self.assertIn("Not a valid integer.", str(context.exception))

    def test_lottery_ranking_schema_invalid_winnings(self):
        invalid_data = {
            "lottery_result_id": 1,
            "player_id": 1,
            "rank": 1,
            "score": 100,
            "winnings": "invalid_winnings",
        }
        with self.assertRaises(ValidationError) as context:
            self.lottery_ranking_schema.load(invalid_data)
        self.assertIn("Not a valid number.", str(context.exception))


if __name__ == "__main__":
    unittest.main()
