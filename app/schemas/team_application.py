from pydantic import BaseModel
from typing import Optional
from enum import Enum
from app.models.team_application import ApplicationType


class ApplicationStatus(str, Enum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"

class ApplicationTypes(str, Enum):
    INVITATION = "INVITATION"
    APPLICATION = "APPLICATION"


class TeamApplicationCreate(BaseModel):
    player_id: int
    team_id: int
    message: Optional[str] = None
    types: Optional[ApplicationType] = ApplicationType.APPLICATION

    class Config:
        use_enum_values = True


class TeamApplicationUpdate(BaseModel):
    status: ApplicationStatus
