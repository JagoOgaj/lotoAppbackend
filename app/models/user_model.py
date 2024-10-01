from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from app.extensions import pwd_context, db
from datetime import datetime
from app.tools import Roles
import re


class User(db.Model):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    _first_name = Column("first_name", String, nullable=False)
    _last_name = Column("last_name", String, nullable=False)
    _email = Column("email", String, unique=True, nullable=False)
    _password_hash = Column("password_hash", String, nullable=False)
    _role_id = Column("role_id", Integer, ForeignKey(
        'roles.id'), default=Roles.USER)
    _notification = Column("notification", Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    role = relationship("Role", back_populates="users")
    entries = relationship('Entry', back_populates='user')

    @hybrid_property
    def first_name(self):
        return self._first_name

    @first_name.setter
    def first_name(self, value):
        if not value or not value.strip():
            raise ValueError("Le prénom ne peut pas être vide.")
        self._first_name = value.strip()

    @hybrid_property
    def last_name(self):
        return self._last_name

    @last_name.setter
    def last_name(self, value):
        if not value or not value.strip():
            raise ValueError("Le nom ne peut pas être vide.")
        self._last_name = value.strip()

    @hybrid_property
    def email(self):
        return self._email

    @email.setter
    def email(self, value):
        email_regex = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
        if not re.match(email_regex, value):
            raise ValueError("Format d'email invalide.")
        self._email = value.strip().lower()

    @hybrid_property
    def notification(self):
        return self._notification

    @notification.setter
    def notification(self, value):
        self._notification = value

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
        return self.role.role_name == Roles.ADMIN

    @is_admin.expression
    def is_admin(cls):
        return cls.role.has(role_name=Roles.ADMIN)

    @hybrid_property
    def password_hash(self):
        return self._password_hash

    @password_hash.setter
    def password_hash(self, value):
        self._password_hash = pwd_context.hash(value)
