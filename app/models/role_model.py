from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.extensions import db


class Role(db.Model):
    """
    Représente un rôle d'utilisateur dans le système.

    Cette classe correspond à la table 'roles' dans la base de données.
    Elle stocke les rôles disponibles pour les utilisateurs, permettant de gérer les
    autorisations et les accès au sein de l'application.

    Attributes:
        id (int): Identifiant unique du rôle (clé primaire).
        role_name (str): Nom du rôle, qui doit être unique (ex: "admin", "user", etc.).

    Relationships:
        users (list[User]): Liste des utilisateurs associés à ce rôle.

    Example:
        admin_role = Role(role_name="admin")
    """

    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    role_name = Column(String, unique=True, nullable=False)

    users = relationship("User", back_populates="role")
