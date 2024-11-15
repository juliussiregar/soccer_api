from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import uuid

class CreateFace(BaseModel):
    company_id: uuid.UUID
    employee_id: uuid.UUID
    photo: str  # Foto dalam format string base64 atau URL foto

class UpdateFace(BaseModel):
    company_id: Optional[uuid.UUID]
    employee_id: Optional[uuid.UUID]
    photo: Optional[str] = None

class FaceData(BaseModel):
    id: uuid.UUID
    company_id: uuid.UUID
    employee_id: uuid.UUID
    photo: str
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True  # Mengizinkan ORM Mode
