from pydantic import BaseModel
from typing import Optional

class GuardianCreate(BaseModel):
    name: str
    kartu_keluarga: str
    ktp: str

class GuardianUpdate(BaseModel):
    name: Optional[str] = None
    kartu_keluarga: Optional[str] = None
    ktp: Optional[str] = None
