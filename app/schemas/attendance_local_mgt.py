from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import uuid

class CreateCheckIn(BaseModel):
    visitor_id : uuid.UUID
    full_name: str
    check_in : datetime

class AttendanceLocalVisitor(BaseModel):
    visitor_id : uuid.UUID
    full_name: str
    check_in: datetime

class AttendanceLocalFilter(BaseModel):
    limit: Optional[int] = None
    page: Optional[int] = None
    search: Optional[str] = None