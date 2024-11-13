# schemas/employee.py

from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class EmployeeFilter(BaseModel):
    limit: Optional[int] = None
    page: Optional[int] = None
    search: Optional[str] = None
    company_id: Optional[str] = None

class CreateNewEmployee(BaseModel):
    company_id: Optional[str] = None
    position_id: int
    user_name: str
    nik: str
    email: str

class UpdateEmployee(BaseModel):
    user_name: Optional[str] = None
    nik: Optional[str] = None
    email: Optional[str] = None

class EmployeeData(BaseModel):
    id: str
    company_id: str
    position_id: int
    user_name: str
    nik: str
    email: str
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True
