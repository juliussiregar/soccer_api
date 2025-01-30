from pydantic import BaseModel
from typing import Optional


class PlayerCreate(BaseModel):
    name: str
    position: str
    profile_picture: Optional[str] = None
    age: Optional[int] = None
    jersey_number: Optional[int] = None
    height: Optional[int] = None  # cm
    weight: Optional[int] = None  # kg
    bio: Optional[str] = None


class PlayerUpdate(BaseModel):
    name: Optional[str] = None
    position: Optional[str] = None
    profile_picture: Optional[str] = None
    age: Optional[int] = None
    jersey_number: Optional[int] = None
    height: Optional[int] = None
    weight: Optional[int] = None
    bio: Optional[str] = None
