from datetime import datetime
from pydantic import BaseModel
from typing import Optional


class PlayerUpdate(BaseModel):
    name: Optional[str] = None
    main_position: Optional[str] = None
    second_position: Optional[str] = None
    third_position: Optional[str] = None
    profile_picture: Optional[str] = None
    birth_date: Optional[datetime] = None
    NISN: Optional[int] = None
    dominant_foot: Optional[str] = None
    jersey_number: Optional[int] = None
    height: Optional[int] = None
    weight: Optional[int] = None
    bio: Optional[str] = None
    total_event: Optional[int] = None
    total_match: Optional[int] = None
    playing_time: Optional[int] = None


class PlayerResponse(BaseModel):
    id: int
    name: Optional[str] = None
    main_position: Optional[str] = None
    second_position: Optional[str] = None
    third_position: Optional[str] = None
    profile_picture: Optional[str] = None
    birth_date: Optional[datetime] = None
    NISN: Optional[int] = None
    dominant_foot: Optional[str] = None
    jersey_number: Optional[int] = None
    height: Optional[int] = None
    weight: Optional[int] = None
    bio: Optional[str] = None
    total_event: Optional[int] = None
    total_match: Optional[int] = None
    playing_time: Optional[int] = None