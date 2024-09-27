# app/__init__.py
from flask import Flask
from flask_jwt_extended import JWTManager
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy
from passlib.context import CryptContext
from app.config import Config
from sqlalchemy.orm import declarative_base
from app.routes import user_bp, admin_bp

# Init attributs
Base = declarative_base()
db: SQLAlchemy = SQLAlchemy(model_class=Base)
ma: Marshmallow = Marshmallow()
jwt: JWTManager = JWTManager()
pwd_context: CryptContext = CryptContext(
    schemes=["pbkdf2_sha256"], deprecated="auto")


def create_app() -> Flask:
    app: Flask = Flask(__name__)
    app.config.from_object(Config)

    # Init Extension
    db.init_app(app)
    jwt.init_app(app)
    ma.init_app(app)

    # Init Blueprint
    app.register_blueprint(user_bp, url_prefix='/user')
    app.register_blueprint(admin_bp, url_prefix='/admin')

    return app
