from pydantic import BaseModel
from typing import Optional
from datetime import datetime, time
import uuid

class CompanyFilter(BaseModel):
    limit: Optional[int] = None
    page: Optional[int] = None
    search: Optional[str] = None

class CreateNewCompany(BaseModel):
    name: str
    logo: Optional[str] = None
    start_time: time
    end_time: time
    max_late: Optional[int] = None

class UpdateCompany(BaseModel):
    name: Optional[str] = None
    logo: Optional[str] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    max_late: Optional[int] = None

class CreateFaceGalleryCompany(BaseModel):
    id: uuid.UUID

class CompanyData(BaseModel):
    id: uuid.UUID
    name: str
    logo: Optional[str]
    start_time: time
    end_time: time
    max_late: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True
