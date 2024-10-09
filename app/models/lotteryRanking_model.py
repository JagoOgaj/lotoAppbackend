from sqlalchemy import Column, Integer, ForeignKey, Float
from sqlalchemy.orm import relationship
from app.extensions import db


class LotteryRanking(db.Model):
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
