from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.extensions import db


class Role(db.Model):
    __tablename__ = 'roles'

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True)
    role_name = Column(
        String,
        unique=True,
        nullable=False)

    users = relationship(
        "User", back_populates="role")
