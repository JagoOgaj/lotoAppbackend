from sqlalchemy import Column, Integer, ForeignKey, String
from sqlalchemy.orm import relationship
from app.extensions import db


class Entry(db.Model):
    """
    Représente une inscription d'un utilisateur à une loterie.

    Cette classe correspond à la table 'entries' dans la base de données.
    Elle stocke les informations relatives à l'inscription d'un utilisateur
    à une loterie, y compris les numéros choisis et les numéros chance.

    Attributes:
        id (int): Identifiant unique de l'inscription (clé primaire).
        user_id (int): Identifiant de l'utilisateur qui a fait l'inscription (clé étrangère).
        lottery_id (int): Identifiant de la loterie à laquelle l'utilisateur s'inscrit (clé étrangère).
        numbers (str): Numéros choisis par l'utilisateur pour la loterie.
        lucky_numbers (str): Numéros chance choisis par l'utilisateur.

    Relationships:
        user (User): Relation vers l'utilisateur qui a fait l'inscription.
        lottery (Lottery): Relation vers la loterie à laquelle l'inscription appartient.

    Methods:
        __repr__(): Retourne une représentation en chaîne de l'objet Entry.

    Example:
        entry = Entry(user_id=1, lottery_id=2, numbers="5,10,15,20,25", lucky_numbers="3,7")
    """

    __tablename__ = "entries"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    lottery_id = Column(Integer, ForeignKey("lotteries.id"), nullable=False)
    numbers = Column(String, nullable=False)
    lucky_numbers = Column(String, nullable=False)

    user = relationship("User", back_populates="entries")
    lottery = relationship("Lottery", back_populates="entries")
