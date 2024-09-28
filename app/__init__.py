# app/__init__.py
from flask import Flask
from app.config import Config
from app.controllers import user_bp, admin_bp, auth_bp
from app.extensions import db, jwt, ma


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
    app.register_blueprint(auth_bp, url_prefix='/auth')

    return app
