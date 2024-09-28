from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from sqlalchemy.ext.hybrid import hybrid_property
from app.extensions import db
from sqlalchemy import func


class Lottery(db.Model):
    __tablename__ = 'lotteries'

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    _name = Column("name", String, nullable=False)
    _start_date = Column("start_date", DateTime, nullable=False)
    _end_date = Column("end_date", DateTime, nullable=False)
    _status = Column("status", String, nullable=False)
    _reward_price = Column("reward_price", Integer, nullable=False)
    _max_participants = Column("max_participants", Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    entries = relationship('Entry', back_populates='lottery')
    results = relationship(
        'LotteryResult', back_populates='lottery', uselist=False)

    @property
    def name(self):
        return self._name

    @property
    def start_date(self):
        return self._start_date

    @property
    def end_date(self):
        return self._end_date

    @property
    def status(self):
        return self._status

    @property
    def reward_price(self):
        return self._reward_price

    @property
    def max_participants(self):
        return self._max_participants

    @property
    def participant_count(self):
        return len(self.entries)

    @hybrid_property
    def is_active(self):
        return self.start_date <= datetime.now() <= self.end_date

    @is_active.expression
    def is_active(cls):
        return func.now().between(cls._start_date, cls._end_date)
