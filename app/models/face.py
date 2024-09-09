import uuid
from .base import Base

from sqlalchemy import UUID, Column, ForeignKey, Integer, String, DateTime, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from app.core.constants.app import DEFAULT_TZ

class Faces(Base):
    __tablename__ = "faces"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    client_id = Column(UUID(as_uuid=True),ForeignKey("visitors.id"), nullable=False)
    visitor_id = Column(UUID(as_uuid=True), ForeignKey("clients.id"), nullable=False)
    image_base64 = Column(String,nullable=False)
    created_at = Column(DateTime, server_default=func.timezone(DEFAULT_TZ, func.now()))
    updated_at = Column(DateTime, nullable=True)

    client = relationship("Client", back_populates="face")
    visitor = relationship("Visitor", back_populates="face")
