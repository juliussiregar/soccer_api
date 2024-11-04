import uuid
from .base import Base

from sqlalchemy import UUID, Column, ForeignKey, Integer, String, DateTime, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from app.core.constants.app import DEFAULT_TZ

class Visitor(Base):
    __tablename__ = "visitors"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String,nullable=True)
    nik = Column(String, unique=True, index=True, nullable=False)
    born_date = Column(DateTime)
    email = Column(String, unique=True, nullable=True)
    address = Column(String,nullable=True)
    company = Column(String, nullable=True)
    client_id = Column(UUID(as_uuid=True), ForeignKey("clients.id"), nullable=False)
    created_at = Column(DateTime, server_default=func.timezone(DEFAULT_TZ, func.now()))
    updated_at = Column(DateTime, nullable=True)

    face = relationship("Faces", back_populates="visitor")
    transaction = relationship("Transaction",back_populates="visitor")
    attendance = relationship("Attendance",back_populates="visitor")
    attendance_local = relationship("AttendanceLocal",back_populates="visitor")
    client = relationship("Client", back_populates="visitor")



    