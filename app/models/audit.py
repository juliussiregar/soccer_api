from .base import Base
from sqlalchemy import Column, Integer, String, SmallInteger, DateTime, func, Float
from sqlalchemy.dialects.postgresql import JSONB
from app.core.constants.app import DEFAULT_TZ


class ApiLog(Base):
    __tablename__ = "perf_logs"
    id = Column(Integer, primary_key=True)
    method = Column(String, nullable=False)
    url = Column(String, nullable=False)
    req_headers = Column(JSONB, nullable=True)
    req_body = Column(JSONB, nullable=True)
    resp_status = Column(SmallInteger, default=200)
    duration = Column(Float, nullable=True)
    created_at = Column(DateTime, server_default=func.timezone(DEFAULT_TZ, func.now()))
