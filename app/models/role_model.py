from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app import Base


class Role(Base):
    __tabename__ = 'roles'

    id = Column(Integer, primary_key=True, autoincrement=True)
    role_name = Column(String, unique=True, nullable=False)

    users = relationship("User", back_populates="role")
