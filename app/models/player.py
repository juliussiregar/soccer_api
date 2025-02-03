from .base import Base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func, Text, Enum as SQLAlchemyEnum
from sqlalchemy.orm import relationship
from app.core.constants.app import DEFAULT_TZ
import enum

class PositionPlayerEnum(enum.Enum):
    GOALKEEPER = "GK"  # Kiper
    CENTER_BACK = "CB"  # Bek Tengah
    LEFT_BACK = "LB"  # Bek Kiri
    RIGHT_BACK = "RB"  # Bek Kanan
    LEFT_WING_BACK = "LWB"  # Bek Sayap Kiri
    RIGHT_WING_BACK = "RWB"  # Bek Sayap Kanan
    DEFENSIVE_MIDFIELDER = "DMF"  # Gelandang Bertahan
    CENTRAL_MIDFIELDER = "CM"  # Gelandang Tengah
    ATTACKING_MIDFIELDER = "AMF"  # Gelandang Serang
    LEFT_WINGER = "LW"  # Sayap Kiri
    RIGHT_WINGER = "RW"  # Sayap Kanan
    LEFT_WING_FORWARD = "LWF"  # Penyerang Sayap Kiri
    RIGHT_WING_FORWARD = "RWF"  # Penyerang Sayap Kanan
    SHADOW_STRIKER = "SS"  # Striker Bayangan
    STRIKER = "ST"  # Penyerang Tengah
    SECOND_STRIKER = "SS"  # Penyerang Kedua
    COMPLETE_FORWARD = "CF"  # Striker Serbaguna
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
