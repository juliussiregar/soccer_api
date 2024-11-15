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
    position_id: Optional[int] = None
    hours_rate: Optional[int] = None
    standard_hours: Optional[int] = None
    max_late: Optional[int] = None
    late_deduction: Optional[int] = None
    min_overtime: Optional[int] = None
    overtime_pay: Optional[int] = None

class UpdateDailySalary(BaseModel):
    position_id: Optional[int] = None
    hours_rate: Optional[int] = None
    standard_hours: Optional[int] = None
    max_late: Optional[int] = None
    late_deduction: Optional[int] = None
    min_overtime: Optional[int] = None
    overtime_pay: Optional[int] = None

class DailySalaryData(BaseModel):
    id: int
    company_id: str
    employee_id: Optional[str] = None
    position_id: Optional[int] = None
    hours_rate: Optional[int] = None
    standard_hours: Optional[int] = None
    max_late: Optional[int] = None
    late_deduction: Optional[int] = None
    min_overtime: Optional[int] = None
    overtime_pay: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True
