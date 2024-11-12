from .base import Base

from sqlalchemy import UUID, ForeignKey, Column, Integer, String, DateTime, func
from sqlalchemy.orm import relationship
from .role import user_role_association
from app.core.constants.app import DEFAULT_TZ


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    full_name = Column(String, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=True)
    created_at = Column(DateTime, server_default=func.timezone(DEFAULT_TZ, func.now()))
    updated_at = Column(DateTime, nullable=True)
    deleted_at = Column(DateTime, nullable=True)
    created_by = Column(Integer, nullable=True)

    company = relationship("Company", back_populates="user")
    roles = relationship(
        "Role", secondary=user_role_association, back_populates="users"
    )

