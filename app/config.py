import os
from dotenv import load_dotenv
from datetime import timedelta

load_dotenv()


class Config:
    """
    Configuration de l'application Flask.

    Cette classe contient les configurations nécessaires pour l'application Flask,
    y compris les paramètres de base de données, les paramètres JWT et les informations
    d'email. Les valeurs de configuration sont extraites des variables d'environnement
    pour garantir la sécurité et la flexibilité dans les différents environnements.

    Attributs:
        FLASK_ENV (str): L'environnement dans lequel l'application s'exécute
                         (par exemple, développement, production).

        SQLALCHEMY_DATABASE_URI (str): URI de connexion à la base de données,
                                        utilisée par SQLAlchemy pour se connecter à la base de données.

        JWT_SECRET_KEY (str): Clé secrète utilisée pour signer les tokens JWT.
                              Elle est essentielle pour la sécurité de l'authentification.

        FLASK_DEBUG (str): Indique si le mode débogage est activé (1) ou non (0).
                           Cela permet de faciliter le développement en affichant
                           les erreurs et en rechargeant automatiquement l'application.

        JWT_IDENTITY_CLAIM (str): Clé de revendication utilisée pour identifier
                                   l'utilisateur dans le token JWT. Par défaut,
                                   c'est "user_id".

        JWT_TOKEN_LOCATION (list): Emplacements dans lesquels le token JWT doit être recherché.
                                   Par défaut, il est configuré pour être recherché dans les
                                   en-têtes des requêtes.

        JWT_ACCESS_TOKEN_EXPIRES (timedelta): Durée de validité du token d'accès JWT.
                                                Par défaut, il expire après 20 minutes.

        APP_EMAIL_PASSWORD (str): Mot de passe de l'application pour l'envoi d'emails,
                                  extrait des variables d'environnement pour des raisons de sécurité.

        MAIL_APP (str): Adresse email de l'application, utilisée pour l'envoi d'emails.

        PATH_WHHTMLTOPDF (str): Chemin de l'executable wkhtmltopdf

    Exemple:
        >>> config = Config()
        >>> print(config.SQLALCHEMY_DATABASE_URI)
        "postgresql://username:password@localhost:5432/mydatabase"
    """

    FLASK_ENV = os.environ.get("FLASK_ENV")
    SQLALCHEMY_DATABASE_URI = os.environ.get("SQLALCHEMY_DATABASE_URI")
    JWT_SECRET_KEY: str = os.environ.get("JWT_SECRET_KEY")
    FLASK_DEBUG: str = os.environ.get("FLASK_DEBUG")
    JWT_IDENTITY_CLAIM: str = "user_id"
    JWT_TOKEN_LOCATION: str = ["headers"]
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=20)
    APP_EMAIL_PASSWORD: str = os.environ.get("APP_PASSWORD")
    MAIL_APP: str = os.environ.get("MAIL_APP")
    PATH_WHHTMLTOPDF: str = os.environ.get("PATH_WHHTMLTOPDF")
    PDF_HTML_PATH: str = os.environ.get("PDF_HTML_PATH")
    PDF_CSS_PATH: str = os.environ.get("PDF_CSS_PATH")
