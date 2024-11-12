import uuid
from .base import Base

from sqlalchemy import UUID, Column, ForeignKey, Integer, String, DateTime, func
from sqlalchemy.orm import relationship
from app.core.constants.app import DEFAULT_TZ

class Employee(Base):
    __tablename__ = "employees"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    user_name = Column(String, unique=True, index=True, nullable=False)
    nik = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    position = Column(String,nullable=False)
    created_at = Column(DateTime, server_default=func.timezone(DEFAULT_TZ, func.now()))
    updated_at = Column(DateTime, nullable=True)
    deleted_at = Column(DateTime, nullable=True)

    company = relationship("Company", back_populates="employee")
    face = relationship("Face", back_populates="employee")
    attendance = relationship("Attendance", back_populates="employee")
    application = relationship("Application", back_populates="employee")
    daily_salary = relationship("DailySalary", back_populates="employee")
    employee_daily_salary = relationship("EmployeeDailySalary", back_populates="employee")
    employee_monthly_salary = relationship("EmployeeMonthlySalary", back_populates="employee")