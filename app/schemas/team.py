from datetime import datetime
from pydantic import BaseModel
from typing import Optional


class TeamCreate(BaseModel):
    team_name: str
    team_logo: Optional[str] = None
    founded_at: Optional[datetime] = None
    basecamp: Optional[str] = None
    contact: Optional[str] = None
    description: Optional[str] = None

    # Data Official yang akan langsung dimasukkan saat membuat tim
    position: str 


class TeamUpdate(BaseModel):
    team_name: Optional[str] = None
    team_logo: Optional[str] = None
    founded_at: Optional[datetime] = None
    basecamp: Optional[str] = None
    contact: Optional[str] = None
    total_players: Optional[int] = None
    description: Optional[str] = None
    
class TeamOfficialAssign(BaseModel):
    team_id: int
    official_id: int
