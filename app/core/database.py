from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
from typing import Iterator
from app.core.config import settings

# Create database engine
engine = create_engine(
    str(settings.database_uri),
    pool_pre_ping=True,  # Checks connection health before each use
    pool_recycle=3600,   # Avoid stale connections (1 hour)
    max_overflow=20,     # Maximum additional connections beyond pool size
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@contextmanager
def get_session() -> Iterator[Session]:
    """Database session generator."""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()
