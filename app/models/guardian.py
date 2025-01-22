from .base import Base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func, Text
from sqlalchemy.orm import relationship
from app.core.constants.app import DEFAULT_TZ


class Guardian(Base):
    __tablename__ = "guardians"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"),unique=True, nullable=False)  # Referensi ke tabel User
    name = Column(String, nullable=False)
    kartu_keluarga = Column(String, nullable=False)
    ktp = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.timezone(DEFAULT_TZ, func.now()))
    updated_at = Column(DateTime, nullable=True)

    # Relasi ke tabel User
    user = relationship("User", back_populates="guardian_profile")
    
    # Relasi ke GuardianPlayer
    guardian_players = relationship("GuardianPlayer", back_populates="guardian", cascade="all, delete-orphan")

