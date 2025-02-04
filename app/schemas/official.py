from pydantic import BaseModel
from typing import Optional


class OfficialCreate(BaseModel):
    name: str
    position: str
    profile_picture: Optional[str] = None


class OfficialUpdate(BaseModel):
    name: Optional[str] = None
    position: Optional[str] = None
    profile_picture: Optional[str] = None
    
class OfficialResponse(BaseModel):
    id: int
    name: str
    position: str
    profile_picture: Optional[str] = None

