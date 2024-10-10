from flask_jwt_extended import JWTManager
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy
from passlib.context import CryptContext
from sqlalchemy.orm import declarative_base

"""
Configuration des extensions de l'application.

Ce module configure plusieurs extensions utilisées dans l'application Flask, 
notamment SQLAlchemy pour la gestion des bases de données, Marshmallow pour la 
sérialisation/désérialisation des données, JWTManager pour la gestion des tokens JWT, 
et CryptContext pour le hachage des mots de passe.

Attributs:
    Base (declarative_base): Classe de base pour tous les modèles SQLAlchemy. 
                             Utilisée pour déclarer des modèles ORM (Object-Relational Mapping).
                             
    db (SQLAlchemy): Instance de SQLAlchemy utilisée pour interagir avec la base de données. 
                     Elle permet de créer, lire, mettre à jour et supprimer des enregistrements dans 
                     la base de données en utilisant les modèles définis avec `Base`.
                     
    ma (Marshmallow): Instance de Marshmallow utilisée pour la sérialisation et 
                      la désérialisation des objets Python en JSON et vice-versa. 
                      Permet également de valider les données entrantes.

    jwt (JWTManager): Instance de JWTManager utilisée pour gérer l'authentification par token JWT. 
                      Elle fournit des méthodes pour créer, vérifier et gérer les tokens JWT.

    pwd_context (CryptContext): Instance de CryptContext utilisée pour le hachage et la vérification 
                                des mots de passe. Supporte plusieurs algorithmes de hachage, 
                                ici configuré pour utiliser `pbkdf2_sha256` pour assurer la sécurité 
                                des mots de passe stockés.

Exemple d'utilisation:
    >>> from app import db, ma
    >>> db.create_all()  # Crée toutes les tables de la base de données
    >>> user_schema = ma.Schema.from_dict(UserSchema)  # Crée un schéma Marshmallow à partir d'un modèle
"""
Base = declarative_base()
db: SQLAlchemy = SQLAlchemy(model_class=Base)
ma: Marshmallow = Marshmallow()
jwt: JWTManager = JWTManager()
pwd_context: CryptContext = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
