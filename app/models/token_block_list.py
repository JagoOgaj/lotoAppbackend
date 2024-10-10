from app.extensions import db
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey


class TokenBlockList(db.Model):
    """
    Représente un jeton bloqué dans la base de données.

    Cette classe correspond à la table 'token_block_list' et est utilisée pour
    gérer les jetons JWT qui ont été révoqués ou bloqués, afin d'empêcher leur
    utilisation future. Cela permet d'assurer la sécurité des sessions utilisateurs
    et de gérer les déconnexions.

    Attributes:
        id (int): Identifiant unique du jeton bloqué (clé primaire).
        jti (str): Identifiant de jeton (JWT ID), qui doit être unique.
        token_type (str): Type du jeton (ex: "access", "refresh").
        user_id (int): Identifiant de l'utilisateur auquel le jeton est associé.
        revoked_at (datetime): Date et heure de la révocation du jeton.
        expires (datetime): Date et heure d'expiration du jeton.

    Relationships:
        user (User): L'utilisateur associé à ce jeton.

    Example:
        blocked_token = TokenBlockList(jti="12345", token_type="access", user_id=1, expires=datetime.utcnow() + timedelta(days=30))
    """

    __tablename__ = "token_block_list"
    id = Column(Integer, primary_key=True, autoincrement=True)
    jti = Column(String, nullable=False, unique=True)
    token_type = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    revoked_at = Column(DateTime)
    expires = Column(DateTime, nullable=False)

    user = db.relationship("User")
