# schemas/application.py

from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime

class ApplicationFilter(BaseModel):
    limit: Optional[int] = None
    page: Optional[int] = None
    employee_id: Optional[str] = None
    company_id: Optional[str] = None

class CreateNewApplication(BaseModel):
    employee_id: str
    location: str
    status: Optional[Literal["Submitted", "Accepted", "Rejected"]] = "Submitted"
    description: str
    
class CreateWFHNewApplication(BaseModel):
    employee_id: str
    location: str
    status: Optional[Literal["Submitted", "Accepted", "Rejected"]] = "Submitted"
    description: str

class UpdateApplication(BaseModel):
    location: Optional[str] = None
    status: Optional[Literal["Submitted", "Accepted", "Rejected"]] = Field(
        None, description="Only 'Submitted', 'Accepted', or 'Rejected' are allowed"
    )
    description: Optional[str] = None

class ApplicationData(BaseModel):
    id: int
    employee_id: str
    location: str
    status: str
    description: str
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True
