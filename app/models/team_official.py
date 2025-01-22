# team_official.py
from .base import Base
from sqlalchemy import UUID, ForeignKey, Column, Integer, String, DateTime, func, UniqueConstraint
from sqlalchemy.orm import relationship
from app.core.constants.app import DEFAULT_TZ

class TeamOfficial(Base):
    __tablename__ = "team_officials"

    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)  # Referensi ke tabel teams
    official_id = Column(Integer, ForeignKey("officials.id"), nullable=False, unique=True)  
    created_at = Column(DateTime, server_default=func.timezone(DEFAULT_TZ, func.now()))

   # Relasi ke Official
    official = relationship("Official", back_populates="team_official")
    
   # Relasi ke Team
    team = relationship("Team", back_populates="team_officials")
    
    __table_args__ = (
        UniqueConstraint("official_id", name="uq_team_official"),  
    )


