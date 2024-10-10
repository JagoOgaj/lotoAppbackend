import unittest
from marshmallow import ValidationError
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
from app.schemas import LotteryCreateSchema, LotteryUpdateSchema
from app.tools import Status


class TestLotteryCreateSchema(unittest.TestCase):
    def setUp(self):
        self.schema = LotteryCreateSchema()

    def test_invalid_reward_price(self):
        with self.assertRaises(ValidationError) as context:
            self.schema.load(
                {
                    "name": "Loterie Test",
                    "status": Status.EN_COUR,
                    "reward_price": 0,
                    "max_participants": 10,
                }
            )
        self.assertIn(
            "{'status': ['Not a valid string.'], 'reward_price': ['La récompence est requis']}",
            str(context.exception),
        )

        with self.assertRaises(ValidationError) as context:
            self.schema.load(
                {
                    "name": "Loterie Test",
                    "status": Status.EN_COUR,
                    "reward_price": "not_a_number",
                    "max_participants": 10,
                }
            )
        self.assertIn(
            "{'status': ['Not a valid string.'], 'reward_price': ['Not a valid integer.']}",
            str(context.exception),
        )


class TestLotteryUpdateSchema(unittest.TestCase):
    def setUp(self):
        self.schema = LotteryUpdateSchema()

    def test_invalid_reward_price(self):
        with self.assertRaises(ValidationError) as context:
            self.schema.load(
                {
                    "reward_price": -50,
                }
            )
        self.assertIn("La recompense doit etre superieur a 0", str(context.exception))

    def test_invalid_status(self):
        with self.assertRaises(ValidationError) as context:
            self.schema.load(
                {
                    "status": "INVALID_STATUS",
                }
            )
        self.assertIn("Mauvais statut du tirage", str(context.exception))


if __name__ == "__main__":
    unittest.main()
