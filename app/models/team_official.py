# team_official.py
from .base import Base
from sqlalchemy import Enum, ForeignKey, Column, Integer, String, DateTime, func, UniqueConstraint, Enum as SQLAlchemyEnum
from sqlalchemy.orm import relationship
from app.core.constants.app import DEFAULT_TZ
import enum

class PositionEnum(enum.Enum):
    # Manajemen Eksekutif
    OWNER = "OWNER"
    CHAIRMAN = "CHAIRMAN"
    HEAD_COACH = "HEAD_COACH"
    ASSISTANT_COACH = "ASSISTANT_COACH"
    FITNESS_COACH = "FITNESS_COACH"
    GOALKEEPING_COACH = "GOALKEEPING_COACH"
    TACTICAL_ANALYST = "TACTICAL_ANALYST"
    TEAM_DOCTOR = "TEAM_DOCTOR"
    YOUTH_COACH = "YOUTH_COACH"
    TALENT_SCOUT = "TALENT_SCOUT"
    GENERAL_MANAGER = "GENERAL_MANAGER"
    MARKETING_DIRECTOR = "MARKETING_DIRECTOR"
    SOCIAL_MEDIA_MANAGER = "SOCIAL_MEDIA_MANAGER"
    EVENT_COORDINATOR = "EVENT_COORDINATOR"
class TeamOfficial(Base):
    __tablename__ = "team_officials"

    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)  # Referensi ke tabel teams
    official_id = Column(Integer, ForeignKey("officials.id"), nullable=False, unique=True)  
    position = Column(SQLAlchemyEnum(PositionEnum), nullable=False)
    created_at = Column(DateTime, server_default=func.timezone(DEFAULT_TZ, func.now()))

   # Relasi ke Official
    official = relationship("Official", back_populates="team_official")
    
   # Relasi ke Team
    team = relationship("Team", back_populates="team_officials")
    
    __table_args__ = (
        UniqueConstraint("official_id", name="uq_team_official"),  
    )


