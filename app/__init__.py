# app/__init__.py
from flask import Flask
from app.config import Config
from app.controllers import user_bp, admin_bp, auth_bp, contact_bp
from app.extensions import db, jwt, ma
from flask_cors import CORS


def create_app() -> Flask:
    """
    Crée et configure une instance de l'application Flask.

    Cette fonction initialise l'application Flask, configure ses paramètres,
    et enregistre les extensions nécessaires et les blueprints.

    Retourne:
        Flask: Une instance de l'application Flask configurée.

    Étapes:
        1. Crée une instance de l'application Flask.
        2. Charge la configuration de l'application à partir de la classe `Config`.
        3. Initialise CORS pour permettre les requêtes entre origines (Cross-Origin Resource Sharing).
        4. Initialise les extensions :
            - SQLAlchemy (db) pour l'interaction avec la base de données.
            - JWTManager (jwt) pour la gestion de l'authentification par token JWT.
            - Marshmallow (ma) pour la sérialisation et la validation des données.
        5. Enregistre les blueprints pour organiser les routes :
            - `user_bp`: routes pour les fonctionnalités utilisateur.
            - `admin_bp`: routes pour les fonctionnalités administratives.
            - `auth_bp`: routes pour l'authentification et la gestion des sessions.
            - `contact_bp`: routes pour les fonctionnalités de contact.

    Exemple d'utilisation:
        >>> app = create_app()  # Crée l'application Flask
        >>> app.run()  # Démarre l'application
    """
    app: Flask = Flask(__name__)
    app.config.from_object(Config)

    # Init Cors
    CORS(app, resources={r"/*": {"origins": "*"}})

    # Init Extension
    db.init_app(app)
    jwt.init_app(app)
    ma.init_app(app)

    # Init Blueprint
    app.register_blueprint(user_bp, url_prefix="/user")
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(contact_bp, url_prefix="/contact")

    return app
