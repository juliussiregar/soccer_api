from .base import Base
from sqlalchemy import UUID, ForeignKey, Column, Integer, String, DateTime, func
from sqlalchemy.orm import relationship
from .role import user_role_association
from app.core.constants.app import DEFAULT_TZ

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=True)
    created_at = Column(DateTime, server_default=func.timezone(DEFAULT_TZ, func.now()))
    updated_at = Column(DateTime, nullable=True)
    deleted_at = Column(DateTime, nullable=True)

    roles = relationship(
        "Role", secondary=user_role_association, back_populates="users"
    )
    # Relasi ke Player
    player_profile = relationship("Player", back_populates="user", uselist=False)
    # Relasi ke Guardian
    guardian_profile = relationship("Guardian", back_populates="user", uselist=False)
     # Relasi ke Official
    official_profile = relationship("Official", back_populates="user", uselist=False)

    
