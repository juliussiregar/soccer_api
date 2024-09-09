import uuid
from .base import Base

from sqlalchemy import UUID, Column, ForeignKey, Integer, String, DateTime, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from app.core.constants.app import DEFAULT_TZ

class Client(Base):
    __tablename__ = "clients"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    client_name = Column(String, unique=True, index=True, nullable=False)
    created_at = Column(DateTime, server_default=func.timezone(DEFAULT_TZ, func.now()))
    updated_at = Column(DateTime, nullable=True)

    face = relationship("Faces", back_populates="client")
    transaction = relationship("Transaction",back_populates="client")
    attandance = relationship("Attendance",back_populates="client")
    visitor = relationship("Visitor",back_populates="client")