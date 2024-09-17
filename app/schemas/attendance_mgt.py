from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import uuid

class CreateCheckIn(BaseModel):
    client_id : uuid.UUID
    visitor_id : uuid.UUID
    check_in : datetime

class UpdateCheckOut(BaseModel):
    client_id : uuid.UUID
    visitor_id : uuid.UUID
    check_out : datetime

class AttendaceVisitor(BaseModel):
    visitor_id : uuid.UUID
    client_id: uuid.UUID
    check_in:datetime
    check_out:datetime