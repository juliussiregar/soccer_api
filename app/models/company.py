import uuid
from .base import Base

from sqlalchemy import UUID, Column, String, DateTime, func
from sqlalchemy.orm import relationship
from app.core.constants.app import DEFAULT_TZ

class Company(Base):
    __tablename__ = "companies"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, unique=True, nullable=False)
    logo = Column(String, nullable=True)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    created_at = Column(DateTime, server_default=func.timezone(DEFAULT_TZ, func.now()))
    updated_at = Column(DateTime, nullable=True)
    deleted_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="company")
    face = relationship("Face", back_populates="company")
    employee = relationship("Employee", back_populates="company")
    position = relationship("Position", back_populates="company")
    attendance = relationship("Attendance", back_populates="company")
    daily_salary = relationship("DailySalary", back_populates="company")
