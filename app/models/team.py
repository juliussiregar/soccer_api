from .base import Base
from sqlalchemy import UUID, ForeignKey, Column, Integer, String, DateTime, func
from sqlalchemy.orm import relationship
from app.core.constants.app import DEFAULT_TZ

class Team(Base):
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, index=True)
    team_name = Column(String, nullable=False)
    team_logo = Column(String, nullable=True)
    coach_name = Column(String, nullable=True)
    total_players = Column(Integer, nullable=True)
    created_at = Column(DateTime, server_default=func.timezone(DEFAULT_TZ, func.now()))
    updated_at = Column(DateTime, nullable=True)
    deleted_at = Column(DateTime, nullable=True)

     # Relasi ke TeamPlayer
    team_players = relationship("TeamPlayer", back_populates="team", cascade="all, delete-orphan")
    team_officials = relationship("TeamOfficial", back_populates="team", cascade="all, delete-orphan")
    # Relasi ke TeamApplication
    team_applications = relationship("TeamApplication", back_populates="team", cascade="all, delete-orphan")

