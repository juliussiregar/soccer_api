from .base import Base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func, Text, Enum as SQLAlchemyEnum
from sqlalchemy.orm import relationship
from app.core.constants.app import DEFAULT_TZ
import enum

import enum

class PositionPlayerEnum(enum.Enum):
    GK = "GK"   # Goalkeeper
    CB = "CB"   # Center Back
    LB = "LB"   # Left Back
    RB = "RB"   # Right Back
    LWB = "LWB" # Left Wing Back
    RWB = "RWB" # Right Wing Back
    DMF = "DMF" # Defensive Midfielder
    CM = "CM"   # Central Midfielder
    AMF = "AMF" # Attacking Midfielder
    LW = "LW"   # Left Winger
    RW = "RW"   # Right Winger
    LWF = "LWF" # Left Wing Forward
    RWF = "RWF" # Right Wing Forward
    SS = "SS"   # Shadow Striker
    ST = "ST"   # Striker
    CF = "CF"   # Complete Forward

class DominantFootEnum(enum.Enum):
    LEFT = "Left"
    RIGHT = "Right"
    BOTH = "Both"

class Player(Base):
    __tablename__ = "players"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"),unique=True, nullable=False)  # Referensi ke tabel User
    name = Column(String, nullable=False)
    main_position = Column(SQLAlchemyEnum(PositionPlayerEnum), nullable=False)
    second_position = Column(SQLAlchemyEnum(PositionPlayerEnum), nullable=False)
    third_position = Column(SQLAlchemyEnum(PositionPlayerEnum), nullable=True)
    profile_picture = Column(String, nullable=True)
    birth_date = Column(DateTime, nullable=False)
    jersey_number = Column(Integer, nullable=True)
    NISN = Column(Integer, nullable=True)
    dominant_foot = Column(SQLAlchemyEnum(DominantFootEnum), nullable=True, default=DominantFootEnum.RIGHT)
    height = Column(Integer, nullable=True)  # Tinggi badan dalam cm
    weight = Column(Integer, nullable=True)  # Berat badan dalam kg
    bio = Column(Text, nullable=True)  # Deskripsi singkat
    total_event = Column(Integer, nullable=False, default=0)  
    total_match = Column(Integer, nullable=False, default=0)  
    playing_time = Column(Integer, nullable=False, default=0)  
    created_at = Column(DateTime, server_default=func.timezone(DEFAULT_TZ, func.now()))
    updated_at = Column(DateTime, nullable=True)

    # Relasi ke tabel User
    user = relationship("User", back_populates="player_profile")
    
    # Relasi ke GuardianPlayer
    guardian_player = relationship("GuardianPlayer", back_populates="player", uselist=False)
    
    # Relasi ke TeamPlayer
    team_player = relationship("TeamPlayer", back_populates="player", uselist=False)
    
    # Relasi ke TeamApplication
    team_applications = relationship("TeamApplication", back_populates="player", cascade="all, delete-orphan")
