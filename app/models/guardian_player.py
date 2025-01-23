# guardian_player.py
from .base import Base
from sqlalchemy import UUID, ForeignKey, Column, Integer, String, DateTime, func, UniqueConstraint
from sqlalchemy.orm import relationship
from app.core.constants.app import DEFAULT_TZ

class GuardianPlayer(Base):
    __tablename__ = "guardian_players"

    id = Column(Integer, primary_key=True, index=True)
    guardian_id = Column(Integer, ForeignKey("guardians.id"), nullable=False) 
    player_id = Column(Integer, ForeignKey("players.id"), nullable=False)  
    created_at = Column(DateTime, server_default=func.timezone(DEFAULT_TZ, func.now()))
    
    # Relasi ke Guardian
    guardian = relationship("Guardian", back_populates="guardian_players")
    
    # Relasi ke Player
    player = relationship("Player", back_populates="guardian_player")

    __table_args__ = (
        UniqueConstraint("player_id", name="uq_guardian_player"), 
    )


