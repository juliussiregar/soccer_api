# schemas/employee.py
import uuid

from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
from uuid import UUID


class EmployeeFilter(BaseModel):
    limit: Optional[int] = None
    page: Optional[int] = None
    search: Optional[str] = None
    company_id: Optional[uuid.UUID] = None

class CreateNewEmployee(BaseModel):
    company_id: Optional[str] = None
    position_id: int
    user_name: str
    nik: str
    email: str
    photo: Optional[str] = None

class UpdateEmployee(BaseModel):
    user_name: Optional[str] = None
    nik: Optional[str] = None
    email: Optional[str] = None
    photo: Optional[str] = None

class EmployeeData(BaseModel):
    id: uuid.UUID
    company_id: uuid.UUID
    position_id: int
    user_name: str
    nik: str
    email: str
    photo: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime]

    # Validator to convert UUID fields to string
    @validator('id', 'company_id', pre=True, always=True)
    def convert_uuid_to_str(cls, v):
        return str(v) if isinstance(v, UUID) else v

    class Config:
        from_attributes = True
