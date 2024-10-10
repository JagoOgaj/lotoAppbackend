import unittest
from marshmallow import ValidationError
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
from app.schemas import (
    UserCreateSchema,
    UserUpdateSchema,
    UserPasswordUpdateSchema,
    UserOverviewInfoSchema,
    UserOverviewAdvancedSchema,
    UserLoginSchema,
)


class TestUserSchemas(unittest.TestCase):
    def setUp(self):
        self.user_create_schema = UserCreateSchema()
        self.user_update_schema = UserUpdateSchema()
        self.user_password_update_schema = UserPasswordUpdateSchema()
        self.user_login_schema = UserLoginSchema()
        self.user_overview_info_schema = UserOverviewInfoSchema()
        self.user_overview_advanced_schema = UserOverviewAdvancedSchema()

    def test_user_create_schema_valid(self):
        valid_data = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com",
            "password": "Password123!",
        }
        result = self.user_create_schema.load(valid_data)
        self.assertEqual(result, valid_data)

    def test_user_create_schema_invalid_email(self):
        invalid_data = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "invalid_email",
            "password": "Password123!",
        }
        with self.assertRaises(ValidationError) as context:
            self.user_create_schema.load(invalid_data)
        self.assertIn("Format d'email invalide.", str(context.exception))

    def test_user_create_schema_invalid_password(self):
        invalid_data = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com",
            "password": "pass",
        }
        with self.assertRaises(ValidationError) as context:
            self.user_create_schema.load(invalid_data)
        self.assertIn(
            "Le mot de passe doit contenir au moins 8 caractères.",
            str(context.exception),
        )

    def test_user_update_schema_valid(self):
        valid_data = {
            "first_name": "Jane",
            "last_name": "Doe",
            "email": "jane.doe@example.com",
            "notification": True,
        }
        result = self.user_update_schema.load(valid_data)
        self.assertEqual(result, valid_data)

    def test_user_password_update_schema_valid(self):
        valid_data = {
            "old_password": "OldPassword123!",
            "new_password": "NewPassword123!",
        }
        result = self.user_password_update_schema.load(valid_data)
        self.assertEqual(result, valid_data)

    def test_user_login_schema_valid(self):
        valid_data = {"email": "user@example.com", "password": "Password123!"}
        result = self.user_login_schema.load(valid_data)
        self.assertEqual(result, valid_data)

    def test_user_overview_info_schema_valid(self):
        valid_data = {
            "first_name": "Alice",
            "last_name": "Smith",
            "email": "alice.smith@example.com",
            "notification": True,
        }
        result = self.user_overview_info_schema.load(valid_data)
        self.assertEqual(result, valid_data)


if __name__ == "__main__":
    unittest.main()
