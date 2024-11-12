from .base import Base

from sqlalchemy import UUID, Column, ForeignKey, DateTime, func, String, Integer
from sqlalchemy.orm import relationship
from app.core.constants.app import DEFAULT_TZ

class EmployeeDailySalary(Base):
    __tablename__ = "employee_daily_salary"
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(UUID(as_uuid=True), ForeignKey("employees.id"), nullable=False)
    work_date = Column(DateTime, nullable=False)
    hours_worked = Column(Integer, nullable=True)
    late_deduction = Column(Integer, nullable=True)
    overtime_pay = Column(Integer, nullable=True)
    normal_salary = Column(Integer, nullable=False)
    total_salary = Column(Integer, nullable=False)
    created_at = Column(DateTime, server_default=func.timezone(DEFAULT_TZ, func.now()))
    updated_at = Column(DateTime, nullable=True)
    deleted_at = Column(DateTime, nullable=True)

    employee = relationship("Employee", back_populates="employee_daily_salary")