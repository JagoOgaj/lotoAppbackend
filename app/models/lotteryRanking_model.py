from sqlalchemy import Column, Integer, ForeignKey, Float
from sqlalchemy.orm import relationship
from app.extensions import db


class LotteryRanking(db.Model):
    """
    Représente le classement des joueurs dans une loterie.

    Cette classe correspond à la table 'lottery_rankings' dans la base de données.
    Elle stocke les informations relatives au classement des joueurs, y compris
    le résultat de la loterie auquel ils sont associés, leur score et leurs gains.

    Attributes:
        id (int): Identifiant unique du classement (clé primaire).
        lottery_result_id (int): Identifiant du résultat de la loterie auquel ce classement est associé.
        player_id (int): Identifiant du joueur (utilisateur) qui a obtenu ce classement.
        rank (int): Classement du joueur pour ce tirage (1 étant le meilleur).
        score (int): Score obtenu par le joueur pour ce tirage.
        winnings (float): Montant des gains associés au classement du joueur.

    Relationships:
        lottery_result (LotteryResult): Résultat de la loterie associé à ce classement.
        player (User): Joueur (utilisateur) associé à ce classement.

    Example:
        ranking = LotteryRanking(lottery_result_id=1, player_id=10, rank=1, score=100, winnings=500.0)
    """

    __tablename__ = "lottery_rankings"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    lottery_result_id = Column(
        Integer, ForeignKey("lottery_results.id"), nullable=False
    )
    player_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    rank = Column(Integer, nullable=False)
    score = Column(Integer, nullable=False)
    winnings = Column(Float, nullable=False)

    lottery_result = relationship("LotteryResult", back_populates="rankings")
    player = relationship("User")
