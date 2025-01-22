from pydantic import BaseModel
from typing import Optional

class TeamCreate(BaseModel):
    team_name: str
    team_logo: Optional[str] = None
    coach_name: Optional[str] = None
    total_players: Optional[int] = 0

class TeamUpdate(BaseModel):
    team_name: Optional[str] = None
    team_logo: Optional[str] = None
    coach_name: Optional[str] = None
    total_players: Optional[int] = None
