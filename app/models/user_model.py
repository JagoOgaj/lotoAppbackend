from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from app import pwd_context
from app import Base
from datetime import datetime


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    _first_name = Column(String, nullable=False)
    _last_name = Column(String, nullable=False)
    _email = Column(String, unique=True, nullable=False)
    _password_hash = Column("password_hash", String, nullable=False)
    _role_id = Column(Integer, ForeignKey('roles.id'), default=2)
    created_at = Column(DateTime, default=datetime.now)
    update_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    role = relationship("Role", back_populates="users")
    entries = relationship('Entry', back_populates='user')

    @hybrid_property
    def email(self):
        return self._email

    @hybrid_property
    def full_name(self):
        return f"{self._first_name} {self._last_name}"

    @hybrid_property
    def role_name(self):
        return self.role.role_name if self.role else None

    @role_name.expression
    def role_name(cls):
        return cls.role.has()

    @hybrid_property
    def is_admin(self):
        return self.role.role_name == "admin"

    @is_admin.expression
    def is_admin(cls):
        return cls.role.has(role_name="admin")

    @hybrid_property
    def password_hash(self):
        return self._password_hash

    @password_hash.setter
    def password_hash(self, value):
        self._password_hash = pwd_context.hash(value)
