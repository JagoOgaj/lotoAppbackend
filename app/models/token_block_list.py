from app.extensions import db
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey


class TokenBlockList(db.Model):
    __tablename__ = "token_block_list"
    id = Column(Integer, primary_key=True, autoincrement=True)
    jti = Column(String, nullable=False, unique=True)
    token_type = Column(String, nullable=False)
    user_id = Column(
        Integer, ForeignKey("users.id"), nullable=False, index=True
    )
    revoked_at = Column(DateTime)
    expires = Column(DateTime, nullable=False)

    user = db.relationship("User")
