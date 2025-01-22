# team_player.py
from .base import Base
from sqlalchemy import UUID, ForeignKey, Column, Integer, String, DateTime, func, UniqueConstraint
from sqlalchemy.orm import relationship
from app.core.constants.app import DEFAULT_TZ

class TeamPlayer(Base):
    __tablename__ = "team_players"

    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)  # Referensi ke tabel teams
    player_id = Column(Integer, ForeignKey("players.id"), nullable=False)  # Referensi ke tabel users sebagai player
    created_at = Column(DateTime, server_default=func.timezone(DEFAULT_TZ, func.now()))

   # Relasi ke Player
    player = relationship("Player", back_populates="team_player")
    
   # Relasi ke Team
    team = relationship("Team", back_populates="team_players")
    
    __table_args__ = (
        UniqueConstraint("player_id", name="uq_team_player"), 
    )


