from .base import Base

from sqlalchemy import UUID, Column, ForeignKey, DateTime, func, String, Integer
from sqlalchemy.orm import relationship
from app.core.constants.app import DEFAULT_TZ

class DailySalary(Base):
    __tablename__ = "daily_salary"
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    employee_id = Column(UUID(as_uuid=True), ForeignKey("employees.id"), nullable=True)
    hours_rate = Column(Integer, nullable=False)
    standard_hours = Column(Integer, nullable=False)
    max_late = Column(Integer, nullable=False)
    late_deduction_rate = Column(Integer, nullable=False)
    min_overtime = Column(Integer, nullable=False)
    overtime_rate = Column(Integer, nullable=False)
    created_at = Column(DateTime, server_default=func.timezone(DEFAULT_TZ, func.now()))
    updated_at = Column(DateTime, nullable=True)
    deleted_at = Column(DateTime, nullable=True)

    company = relationship("Company", back_populates="daily_salary")
    employee = relationship("Employee", back_populates="daily_salary")