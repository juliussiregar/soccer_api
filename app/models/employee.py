import uuid
from .base import Base
from sqlalchemy import UUID, Column, ForeignKey, DateTime, func, String, Integer
from sqlalchemy.orm import relationship
from app.core.constants.app import DEFAULT_TZ

class Employee(Base):
    __tablename__ = "employees"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    position_id = Column(Integer, ForeignKey("positions.id"), nullable=False)  # ForeignKey ke Position.id
    user_name = Column(String, unique=True, index=True, nullable=False)
    nik = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime, server_default=func.timezone(DEFAULT_TZ, func.now()))
    updated_at = Column(DateTime, nullable=True)
    deleted_at = Column(DateTime, nullable=True)

    # Relationships
    company = relationship("Company", back_populates="employee")
    position = relationship("Position", back_populates="employees")  # Relationship ke Position
    face = relationship("Face", back_populates="employee")
    attendance = relationship("Attendance", back_populates="employee")
    application = relationship("Application", back_populates="employee")
    daily_salary = relationship("DailySalary", back_populates="employee")
    employee_daily_salary = relationship("EmployeeDailySalary", back_populates="employee")
    employee_monthly_salary = relationship("EmployeeMonthlySalary", back_populates="employee")
