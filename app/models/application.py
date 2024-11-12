from .base import Base

from sqlalchemy import UUID, Column, ForeignKey, DateTime, func, String, Integer
from sqlalchemy.orm import relationship
from app.core.constants.app import DEFAULT_TZ

class Application(Base):
    __tablename__ = "applications"
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(UUID(as_uuid=True), ForeignKey("employees.id"), nullable=False)
    location = Column(String, nullable=False)
    status = Column(String, nullable=False)
    description = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.timezone(DEFAULT_TZ, func.now()))
    updated_at = Column(DateTime, nullable=True)
    deleted_at = Column(DateTime, nullable=True)

    employee = relationship("Employee", back_populates="application")