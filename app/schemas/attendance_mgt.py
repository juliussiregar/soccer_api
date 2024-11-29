from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
import uuid
import pytz

from app.core.constants.app import DEFAULT_TZ

# Get Jakarta timezone
jakarta_timezone = pytz.timezone(DEFAULT_TZ)

# Function to get current Jakarta time
def current_jakarta_time() -> datetime:
    return datetime.now(jakarta_timezone)

# Function to generate today's date as a string in the desired format
def current_jakarta_time_example() -> str:
    return datetime.now(jakarta_timezone).strftime("%Y-%m-%dT%H:%M:%S")

class AttendanceFilter(BaseModel):
    limit: Optional[int] = None
    page: Optional[int] = None
    search: Optional[str] = None
    company_id: Optional[uuid.UUID] = None

# Create Schema for Check-In
class CreateCheckIn(BaseModel):
    company_id: uuid.UUID
    employee_id: uuid.UUID
    check_in: datetime = Field(default_factory=current_jakarta_time, example=current_jakarta_time_example())
    photo_in: str
    location: Optional[str] = None
    type: Optional[str] = "WFO"

# Update Schema for Check-Out
class UpdateCheckOut(BaseModel):
    company_id: uuid.UUID
    employee_id: uuid.UUID
    check_out: datetime = Field(default_factory=current_jakarta_time, example=current_jakarta_time_example())
    photo_out: str
    location: Optional[str] = None

# Schema for Retrieving Attendance Data
class AttendanceData(BaseModel):
    id: int
    company_id: uuid.UUID
    employee_id: uuid.UUID
    check_in: datetime
    check_out: Optional[datetime]
    photo_in: Optional[str]
    photo_out: Optional[str]
    location: Optional[str]
    type: str
    late: Optional[int] = 0
    overtime: Optional[int] = 0
    description: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

# Full Update Schema for Attendance (CRUD)
class UpdateAttendance(BaseModel):
    company_id: Optional[uuid.UUID]
    employee_id: Optional[uuid.UUID]
    check_in: Optional[datetime] = Field(None, example=current_jakarta_time_example())
    check_out: Optional[datetime] = Field(None, example=current_jakarta_time_example())
    photo_in: Optional[str] = None
    photo_out: Optional[str] = None
    location: Optional[str] = None
    type: Optional[str] = None
    late: Optional[int] = None
    overtime: Optional[int] = None
    description: Optional[str] = None

# Schema for Identifying an Employee via Face
class IdentifyEmployee(BaseModel):
    image: str
    company_id: Optional[str] = None
    location: Optional[str] = None
    token: Optional[str] = None

# Schema for Creating a New Attendance Entry (Generalized)
class CreateAttendance(BaseModel):
    company_id: uuid.UUID
    employee_id: uuid.UUID
    check_in: Optional[datetime] = Field(None, example=current_jakarta_time_example())
    check_out: Optional[datetime] = Field(None, example=current_jakarta_time_example())
    photo_in: Optional[str] = None
    photo_out: Optional[str] = None
    location: Optional[str] = None
    type: Optional[str] = "WFO"
    late: Optional[int] = 0
    overtime: Optional[int] = 0
    description: Optional[str] = None
