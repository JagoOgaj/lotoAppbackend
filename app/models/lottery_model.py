from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from app import Base
from datetime import datetime
from sqlalchemy.ext.hybrid import hybrid_property


class Lottery(Base):
    __tablename__ = 'lotteries'

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    name = Column(String, nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    status = Column(String, nullable=False)
    max_participants = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    entries = relationship('Entry', back_populates='lottery')
    results = relationship(
        'LotteryResult', back_populates='lottery', uselist=False)

    @hybrid_property
    def is_active(self):
        return self.start_date <= datetime.now() <= self.end_date

    @is_active.expression
    def is_active(cls):
        from sqlalchemy import func
        return func.now().between(cls.start_date, cls.end_date)
