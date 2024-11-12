import uuid
from .base import Base

from sqlalchemy import UUID, Column, ForeignKey, String, DateTime, func
from sqlalchemy.orm import relationship
from app.core.constants.app import DEFAULT_TZ

class Face(Base):
    __tablename__ = "faces"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True),ForeignKey("companies.id"), nullable=False)
    employee_id = Column(UUID(as_uuid=True), ForeignKey("employees.id"), nullable=False)
    photo = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.timezone(DEFAULT_TZ, func.now()))
    updated_at = Column(DateTime, nullable=True)
    deleted_at = Column(DateTime, nullable=True)

    company = relationship("Company", back_populates="face")
    employee = relationship("Employee", back_populates="face")
