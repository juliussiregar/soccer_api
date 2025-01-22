from .base import Base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func, Text
from sqlalchemy.orm import relationship
from app.core.constants.app import DEFAULT_TZ


class Player(Base):
    __tablename__ = "players"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"),unique=True, nullable=False)  # Referensi ke tabel User
    name = Column(String, nullable=False)
    position = Column(String, nullable=False)
    profile_picture = Column(String, nullable=True)
    age = Column(Integer, nullable=True)
    jersey_number = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)  # Tinggi badan dalam cm
    weight = Column(Integer, nullable=True)  # Berat badan dalam kg
    bio = Column(Text, nullable=True)  # Deskripsi singkat
    created_at = Column(DateTime, server_default=func.timezone(DEFAULT_TZ, func.now()))
    updated_at = Column(DateTime, nullable=True)

    # Relasi ke tabel User
    user = relationship("User", back_populates="player_profile")
    
    # Relasi ke GuardianPlayer
    guardian_player = relationship("GuardianPlayer", back_populates="player", uselist=False)
    
    # Relasi ke TeamPlayer
    team_player = relationship("TeamPlayer", back_populates="player", uselist=False)
