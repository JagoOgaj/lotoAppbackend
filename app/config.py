import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    POSTGRES_USER: str = os.environ.get('POSTGRES_USER')
    POSTGRES_PASSWORD: str = os.environ.get('POSTGRES_PASSWORD')
    POSTGRES_DB: str = os.environ.get('POSTGRES_DB')
    POSTGRES_HOST: str = os.environ.get('POSTGRES_HOST')
    POSTGRES_PORT: str = os.environ.get('POSTGRES_PORT')
    SQLALCHEMY_DATABASE_URI = f"postgresql://{POSTGRES_USER}:{
        POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
    JWT_SECRET_KEY: str = os.environ.get('JWT_SECRET_KEY')
    FLASK_DEBUG: str = os.environ.get('FLASK_DEBUG')
    JWT_IDENTITY_CLAIM: str = "user_id"
    JWT_TOKEN_LOCATION: str = ["headers"]
