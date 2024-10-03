from flask_jwt_extended import JWTManager
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy
from passlib.context import CryptContext
from sqlalchemy.orm import declarative_base


Base = declarative_base()
db: SQLAlchemy = SQLAlchemy(model_class=Base)
ma: Marshmallow = Marshmallow()
jwt: JWTManager = JWTManager()
pwd_context: CryptContext = CryptContext(
    schemes=["pbkdf2_sha256"], deprecated="auto"
)
