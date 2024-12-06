# schemas/employee_daily_salary.py
import uuid
from decimal import Decimal

import pytz
from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime, date

from app.core.constants.app import DEFAULT_TZ

# Get Jakarta timezone
jakarta_timezone = pytz.timezone(DEFAULT_TZ)

# Function to get current Jakarta time
def current_jakarta_time() -> datetime:
    return datetime.now(jakarta_timezone)

# Function to generate today's date as a string in the desired format
def current_jakarta_time_example() -> str:
    return datetime.now(jakarta_timezone).strftime("%Y-%m-%d")

class EmployeeDailySalaryFilter(BaseModel):
    limit: Optional[int] = None
    page: Optional[int] = None
    search: Optional[str] = None
    employee_id: Optional[uuid.UUID] = None
    company_id: Optional[uuid.UUID] = None

class CreateNewEmployeeDailySalary(BaseModel):
    employee_id: uuid.UUID
    work_date: date = Field(None, example=current_jakarta_time_example())
    hours_worked: Optional[Decimal] = None
    late_deduction: Optional[Decimal] = None
    month: Optional[int] = None
    year: Optional[int] = None
    normal_salary: Optional[Decimal] = None
    total_salary: Optional[Decimal] = None

    @validator('normal_salary', 'total_salary', pre=True, always=True)
    def validate_numeric_precision(cls, value):
        if value is not None:
            # Pastikan presisi tidak melebihi 2 desimal
            if value.as_tuple().exponent < -2:
                raise ValueError("Value exceeds maximum of 2 decimal places")
            # Pastikan total digit tidak melebihi 10
            if len(value.as_tuple().digits) > 10:
                raise ValueError("Value exceeds maximum of 10 digits")
        return value

class UpdateEmployeeDailySalary(BaseModel):
    work_date: datetime = Field(None, example=current_jakarta_time_example())
    hours_worked: Optional[Decimal] = None
    late_deduction: Optional[Decimal] = None
    month: Optional[int] = None
    year: Optional[int] = None
    normal_salary: Optional[Decimal] = None
    total_salary: Optional[Decimal] = None

    @validator('normal_salary', 'total_salary', pre=True, always=True)
    def validate_numeric_precision(cls, value):
        if value is not None:
            # Pastikan presisi tidak melebihi 2 desimal
            if value.as_tuple().exponent < -2:
                raise ValueError("Value exceeds maximum of 2 decimal places")
            # Pastikan total digit tidak melebihi 10
            if len(value.as_tuple().digits) > 10:
                raise ValueError("Value exceeds maximum of 10 digits")
        return value

class EmployeeDailySalaryData(BaseModel):
    id: int
    employee_id: uuid.UUID
    work_date: Optional[int] = None
    hours_worked: Optional[Decimal] = None
    late_deduction: Optional[int] = None
    month: Optional[int] = None
    year: Optional[int] = None
    normal_salary: Optional[Decimal] = None
    total_salary: Optional[Decimal] = None
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True
