from .base import Base

from sqlalchemy import UUID, Column, ForeignKey, DateTime, func, String, Integer
from sqlalchemy.orm import relationship
from app.core.constants.app import DEFAULT_TZ

class Attendance(Base):
    __tablename__ = "attendances"
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    employee_id = Column(UUID(as_uuid=True), ForeignKey("employees.id"), nullable=False)
    check_in = Column(DateTime, nullable=True)
    check_out = Column(DateTime, nullable=True)
    photo_in = Column(String, nullable=True)
    photo_out = Column(String, nullable=True)
    late = Column(Integer, nullable=True)
    overtime = Column(Integer, nullable=True)
    location = Column(String, nullable=True)
    type = Column(String, nullable=False)
    description = Column(String, nullable=True)
    created_at = Column(DateTime, server_default=func.timezone(DEFAULT_TZ, func.now()))
    updated_at = Column(DateTime, nullable=True)
    deleted_at = Column(DateTime, nullable=True)

    company = relationship("Company", back_populates="attendance")
    employee = relationship("Employee", back_populates="attendance")