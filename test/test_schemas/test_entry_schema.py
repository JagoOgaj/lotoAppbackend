import unittest
from marshmallow import ValidationError
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
from app.schemas import (
    EntryOverviewSchema,
    EntryRegistrySchema,
    EntryAdminAddUserSchema,
)
from app.tools import Status


class TestEntryOverviewSchema(unittest.TestCase):
    def setUp(self):
        self.schema = EntryOverviewSchema()

    def test_valid_data(self):
        data = {
            "user_id": 1,
            "user": {"full_name": "John Doe", "email": "john.doe@example.com"},
            "numbers": "5,12,23,34,45",
            "lucky_numbers": "2,8",
        }
        result = self.schema.dump(data)
        self.assertEqual(result["user_id"], 1)
        self.assertEqual(result["user_name"], "John Doe")
        self.assertEqual(result["email"], "john.doe@example.com")
        self.assertEqual(result["numbers"], "5,12,23,34,45")
        self.assertEqual(result["lucky_numbers"], "2,8")


class TestEntryRegistrySchema(unittest.TestCase):
    def setUp(self):
        self.schema = EntryRegistrySchema()

    def test_valid_data(self):
        data = {"lottery_id": 1, "numbers": "5,12,23,34,45", "lucky_numbers": "2,8"}
        validated_data = self.schema.load(data)
        self.assertEqual(validated_data["lottery_id"], 1)
        self.assertEqual(validated_data["numbers"], "5,12,23,34,45")
        self.assertEqual(validated_data["lucky_numbers"], "2,8")

    def test_invalid_numbers_too_few(self):
        with self.assertRaises(ValidationError) as context:
            self.schema.load(
                {"lottery_id": 1, "numbers": "5,12", "lucky_numbers": "2,8"}
            )
        self.assertIn(
            "Il manque des numéros (minimum 5 requis)", str(context.exception)
        )

    def test_invalid_numbers_duplicates(self):
        with self.assertRaises(ValidationError) as context:
            self.schema.load(
                {"lottery_id": 1, "numbers": "5,12,23,34,34", "lucky_numbers": "2,8"}
            )
        self.assertIn("Les numéros doivent être différents", str(context.exception))

    def test_invalid_numbers_out_of_range(self):
        with self.assertRaises(ValidationError) as context:
            self.schema.load(
                {
                    "lottery_id": 1,
                    "numbers": "5,12,23,60,45",  # 60 est hors de portée
                    "lucky_numbers": "2,8",
                }
            )
        self.assertIn("Les numéros doivent être entre 1 et 49", str(context.exception))

    def test_invalid_lucky_numbers_too_many(self):
        with self.assertRaises(ValidationError) as context:
            self.schema.load(
                {
                    "lottery_id": 1,
                    "numbers": "5,12,23,34,45",
                    "lucky_numbers": "2,8,9",  # Trop de numéros chanceux
                }
            )
        self.assertIn(
            "Un maximum de 2 numéros chanceux est autorisé", str(context.exception)
        )


class TestEntryAdminAddUserSchema(unittest.TestCase):
    def setUp(self):
        self.schema = EntryAdminAddUserSchema()

    def test_invalid_numbers_duplicates(self):
        with self.assertRaises(ValidationError) as context:
            self.schema.load(
                {
                    "user_name": "John Doe",
                    "email": "john.doe@example.com",
                    "numbers": "5,12,23,34,34",
                    "numbers_lucky": "2,8",
                }
            )
        self.assertIn("Les numéros doivent être différents", str(context.exception))

    def test_invalid_numbers_out_of_range(self):
        with self.assertRaises(ValidationError) as context:
            self.schema.load(
                {
                    "user_name": "John Doe",
                    "email": "john.doe@example.com",
                    "numbers": "5,12,23,60,45",  # 60 est hors de portée
                    "numbers_lucky": "2,8",
                }
            )
        self.assertIn("Les numéros doivent être entre 1 et 49", str(context.exception))

    def test_invalid_lucky_numbers_too_many(self):
        with self.assertRaises(ValidationError) as context:
            self.schema.load(
                {
                    "user_name": "John Doe",
                    "email": "john.doe@example.com",
                    "numbers": "5,12,23,34,45",
                    "numbers_lucky": "2,8,9",  # Trop de numéros chanceux
                }
            )
        self.assertIn(
            "Un maximum de 2 numéros chanceux est autorisé", str(context.exception)
        )


if __name__ == "__main__":
    unittest.main()
