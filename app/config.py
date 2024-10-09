import os
from dotenv import load_dotenv
from datetime import timedelta

load_dotenv()


class Config:
    FLASK_ENV = os.environ.get("FLASK_ENV")
    SQLALCHEMY_DATABASE_URI = os.environ.get("SQLALCHEMY_DATABASE_URI")
    JWT_SECRET_KEY: str = os.environ.get("JWT_SECRET_KEY")
    FLASK_DEBUG: str = os.environ.get("FLASK_DEBUG")
    JWT_IDENTITY_CLAIM: str = "user_id"
    JWT_TOKEN_LOCATION: str = ["headers"]
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=20)
    APP_EMAIL_PASSWORD: str = os.environ.get("APP_PASSWORD")
    MAIL_APP: str = os.environ.get("MAIL_APP")
