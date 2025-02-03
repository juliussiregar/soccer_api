from .base import Base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func, Enum as SQLAlchemyEnum
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

class Official(Base):
    __tablename__ = "officials"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"),unique=True, nullable=False)  # Referensi ke tabel User
    name = Column(String, nullable=False)
    position = Column(SQLAlchemyEnum(PositionEnum), nullable=False)
    profile_picture = Column(String, nullable=True)
    created_at = Column(DateTime, server_default=func.timezone(DEFAULT_TZ, func.now()))
    updated_at = Column(DateTime, nullable=True)

    # Relasi ke tabel User
    user = relationship("User", back_populates="official_profile")
    
    # Relasi ke TeamPlayer
    team_official = relationship("TeamOfficial", back_populates="official", uselist=False)
