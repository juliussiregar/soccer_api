from pydantic import BaseModel
from typing import Optional
from enum import Enum


class ApplicationStatus(str, Enum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"


class TeamApplicationCreate(BaseModel):
    player_id: int
    team_id: int
    message: Optional[str] = None


class TeamApplicationUpdate(BaseModel):
    status: ApplicationStatus
