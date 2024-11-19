from .base import Base

from sqlalchemy import UUID, Column, ForeignKey, DateTime, func, Integer, Numeric
from sqlalchemy.orm import relationship
from app.core.constants.app import DEFAULT_TZ

class EmployeeMonthlySalary(Base):
    __tablename__ = "employee_monthly_salary"
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(UUID(as_uuid=True), ForeignKey("employees.id"), nullable=False)
    month = Column(Integer, nullable=False)
    year = Column(Integer, nullable=False)
    normal_salary = Column(Numeric(10, 2), nullable=False)
    total_salary = Column(Numeric(10, 2), nullable=False)
    created_at = Column(DateTime, server_default=func.timezone(DEFAULT_TZ, func.now()))
    updated_at = Column(DateTime, nullable=True)
    deleted_at = Column(DateTime, nullable=True)

    employee = relationship("Employee", back_populates="employee_monthly_salary")