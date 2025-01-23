from datetime import datetime
from .base import Base

from sqlalchemy import Column, String, DateTime

class RevokedToken(Base):
    __tablename__ = "revoked_tokens"

    token = Column(String, primary_key=True, nullable=False)
    revoked_at = Column(DateTime, default=datetime.utcnow, nullable=False)
