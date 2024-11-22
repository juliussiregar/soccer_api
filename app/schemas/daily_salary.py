# schemas/daily_salary.py

from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class DailySalaryFilter(BaseModel):
    limit: Optional[int] = None
    page: Optional[int] = None
    company_id: Optional[str] = None

class CreateNewDailySalary(BaseModel):
    company_id: Optional[str] = None
    employee_id: Optional[str] = None
    hours_rate: Optional[int] = None
    standard_hours: Optional[int] = None
    max_late: Optional[int] = None
    late_deduction_rate: Optional[int] = None
    min_overtime: Optional[int] = None
    overtime_rate: Optional[int] = None

class UpdateDailySalary(BaseModel):
    hours_rate: Optional[int] = None
    standard_hours: Optional[int] = None
    max_late: Optional[int] = None
    late_deduction_rate: Optional[int] = None
    min_overtime: Optional[int] = None
    overtime_rate: Optional[int] = None
    
    
class EmployeeData(BaseModel):
    id: str
    full_name: str
    email: Optional[str]

    class Config:
        from_attributes = True

class DailySalaryData(BaseModel):
    id: int
    company_id: str
    employee_id: Optional[str] = None
    employee: Optional[EmployeeData] = None  # Include employee data
    hours_rate: Optional[int] = None
    standard_hours: Optional[int] = None
    max_late: Optional[int] = None
    late_deduction_rate: Optional[int] = None
    min_overtime: Optional[int] = None
    overtime_rate: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True