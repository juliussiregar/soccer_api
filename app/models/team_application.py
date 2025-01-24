from .base import Base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func, Text, Enum
from sqlalchemy.orm import relationship
from app.core.constants.app import DEFAULT_TZ
from enum import Enum as PyEnum

# Status aplikasi
class ApplicationStatus(PyEnum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"

class TeamApplication(Base):
    __tablename__ = "team_applications"

    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(Integer, ForeignKey("players.id"), nullable=False)  # Referensi ke Player
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)  # Referensi ke Team
    status = Column(Enum(ApplicationStatus), default=ApplicationStatus.PENDING, nullable=False)  # Status aplikasi
    message = Column(Text, nullable=True)  # Pesan opsional dari Player
    created_at = Column(DateTime, server_default=func.timezone(DEFAULT_TZ, func.now()))
    updated_at = Column(DateTime, nullable=True)

    # Relasi ke Player
    player = relationship("Player", back_populates="team_applications")

    # Relasi ke Team
    team = relationship("Team", back_populates="team_applications")
