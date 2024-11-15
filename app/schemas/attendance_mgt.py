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

class CreateCheckIn(BaseModel):
    company_id: uuid.UUID
    employee_id: uuid.UUID
    # Provide dynamic example for Swagger using current Jakarta time
    check_in: datetime = Field(default_factory=current_jakarta_time, example=current_jakarta_time_example())
    photo_in: str
    location: Optional[str] = None
    type: Optional[str] = "WFO"

class UpdateCheckOut(BaseModel):
    company_id: uuid.UUID
    employee_id: uuid.UUID
    # Provide dynamic example for Swagger using current Jakarta time
    check_out: datetime = Field(default_factory=current_jakarta_time, example=current_jakarta_time_example())
    photo_out: str
    location: Optional[str] = None

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

class IdentifyEmployee(BaseModel):
    image : str
    company_name:Optional[str] = None
    location: Optional[str] = None