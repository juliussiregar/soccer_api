import enum
from .base import Base
from sqlalchemy import Column, Integer, DateTime, ForeignKey, func, UniqueConstraint, Enum as SQLAlchemyEnum
from sqlalchemy.orm import relationship
from app.core.constants.app import DEFAULT_TZ

class GuardianRelationshipEnum(enum.Enum):
    FATHER = "Father"  # Ayah
    MOTHER = "Mother"  # Ibu
    BROTHER = "Brother"  # Kakak Laki-laki
    SISTER = "Sister"  # Kakak Perempuan
    UNCLE = "Uncle"  # Paman
    AUNT = "Aunt"  # Tante
    GRANDFATHER = "Grandfather"  # Kakek
    GRANDMOTHER = "Grandmother"  # Nenek
    OTHER = "Other"  # Lainnya

class GuardianPlayer(Base):
    __tablename__ = "guardian_players"

    id = Column(Integer, primary_key=True, index=True)
    guardian_id = Column(Integer, ForeignKey("guardians.id"), nullable=False) 
    player_id = Column(Integer, ForeignKey("players.id"), nullable=False)  
    relationship_guardian = Column(SQLAlchemyEnum(GuardianRelationshipEnum), nullable=False)  # Perbaikan di sini
    created_at = Column(DateTime, server_default=func.timezone(DEFAULT_TZ, func.now()))
    
    # Relasi ke Guardian
    guardian = relationship("Guardian", back_populates="guardian_players")
    
    # Relasi ke Player
    player = relationship("Player", back_populates="guardian_player")

    __table_args__ = (
        UniqueConstraint("player_id", name="uq_guardian_player"), 
    )
