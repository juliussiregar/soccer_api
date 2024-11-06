import uuid
from .base import Base

from sqlalchemy import UUID, Column, ForeignKey, DateTime, func, String
from sqlalchemy.orm import relationship
from app.core.constants.app import DEFAULT_TZ

class AttendanceLocal(Base):
    __tablename__ = "attendance_local"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    visitor_id = Column(UUID(as_uuid=True), ForeignKey("visitors.id"), nullable=False)
    full_name = Column(String, nullable=True)
    Check_in = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.timezone(DEFAULT_TZ, func.now()))
    updated_at = Column(DateTime, nullable=True)

    visitor = relationship("Visitor", back_populates="attendance_local")