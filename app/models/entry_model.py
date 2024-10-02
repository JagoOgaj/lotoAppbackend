from sqlalchemy import Column, Integer, ForeignKey, String
from sqlalchemy.orm import relationship
from app.extensions import db


class Entry(db.Model):
    __tablename__ = 'entries'

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        index=True)
    user_id = Column(
        Integer,
        ForeignKey('users.id'),
        nullable=False)
    lottery_id = Column(
        Integer,
        ForeignKey('lotteries.id'),
        nullable=False)
    numbers = Column(
        String, nullable=False)
    lucky_numbers = Column(
        String, nullable=False)

    user = relationship(
        'User', back_populates='entries')
    lottery = relationship(
        'Lottery', back_populates='entries')
