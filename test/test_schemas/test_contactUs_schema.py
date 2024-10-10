import unittest
from marshmallow import ValidationError
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
from app.schemas import ContactUsSchema  # Assurez-vous d'importer votre schéma


class TestContactUsSchema(unittest.TestCase):
    def setUp(self):
        self.schema = ContactUsSchema()

    def test_valid_data(self):
        data = {
            "email": "john.doe@example.com",
            "message": "J'aimerais en savoir plus sur vos services.",
        }
        validated_data = self.schema.load(data)
        self.assertEqual(validated_data["email"], "john.doe@example.com")
        self.assertEqual(
            validated_data["message"], "J'aimerais en savoir plus sur vos services."
        )

    def test_invalid_email_format(self):
        with self.assertRaises(ValidationError) as context:
            self.schema.load(
                {"email": "invalid_email", "message": "Ce message est correct."}
            )
        self.assertIn("Not a valid email address.", str(context.exception))

    def test_empty_message(self):
        with self.assertRaises(ValidationError) as context:
            self.schema.load({"email": "john.doe@example.com", "message": ""})
        self.assertIn(
            "{'message': ['Length must be between 1 and 1000.']", str(context.exception)
        )

    def test_message_too_long(self):
        long_message = "A" * 1001  # 1001 caractères
        with self.assertRaises(ValidationError) as context:
            self.schema.load({"email": "john.doe@example.com", "message": long_message})
        self.assertIn(
            "{'message': ['Length must be between 1 and 1000.']}",
            str(context.exception),
        )

    def test_missing_email(self):
        with self.assertRaises(ValidationError) as context:
            self.schema.load({"message": "Ce message est correct."})
        self.assertIn("Missing data for required field.", str(context.exception))

    def test_missing_message(self):
        with self.assertRaises(ValidationError) as context:
            self.schema.load({"email": "john.doe@example.com"})
        self.assertIn("Missing data for required field.", str(context.exception))

    def test_email_too_long(self):
        long_email = (
            "a" * 256 + "@example.com"
        )  # 256 caractères dans la partie avant l'@
        with self.assertRaises(ValidationError) as context:
            self.schema.load(
                {"email": long_email, "message": "Ce message est correct."}
            )
        self.assertIn(
            "{'email': ['Longer than maximum length 255.']}", str(context.exception)
        )


if __name__ == "__main__":
    unittest.main()
