from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.extensions import db


class LotteryResult(db.Model):
    __tablename__ = "lottery_results"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    lottery_id = Column(Integer, ForeignKey("lotteries.id"), nullable=False)
    winning_numbers = Column(String, nullable=False)
    winning_lucky_numbers = Column(String, nullable=False)

    lottery = relationship("Lottery", back_populates="results")
    rankings = relationship("LotteryRanking", back_populates="lottery_result")
