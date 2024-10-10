from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.extensions import db


class LotteryResult(db.Model):
    """
    Représente le résultat d'un tirage de loterie.

    Cette classe correspond à la table 'lottery_results' dans la base de données.
    Elle stocke les informations relatives aux résultats d'un tirage, y compris
    les numéros gagnants et les numéros chance.

    Attributes:
        id (int): Identifiant unique du résultat (clé primaire).
        lottery_id (int): Identifiant de la loterie associée à ce résultat.
        winning_numbers (str): Numéros gagnants du tirage, stockés sous forme de chaîne
                               (ex: "1,2,3,4,5").
        winning_lucky_numbers (str): Numéros chance du tirage, stockés sous forme de chaîne
                                      (ex: "1,2").

    Relationships:
        lottery (Lottery): Loterie associée à ce résultat.
        rankings (list[LotteryRanking]): Classements des joueurs associés à ce résultat.

    Example:
        result = LotteryResult(lottery_id=1, winning_numbers="5,12,23,34,45", winning_lucky_numbers="2,7")
    """

    __tablename__ = "lottery_results"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    lottery_id = Column(Integer, ForeignKey("lotteries.id"), nullable=False)
    winning_numbers = Column(String, nullable=False)
    winning_lucky_numbers = Column(String, nullable=False)

    lottery = relationship("Lottery", back_populates="results")
    rankings = relationship("LotteryRanking", back_populates="lottery_result")
