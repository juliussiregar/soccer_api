from sqlalchemy import create_engine
from contextlib import contextmanager
from typing import Iterator
from sqlalchemy.orm import Session

from app.core.config import settings

engine = create_engine(
    str(settings.database_uri),
    pool_pre_ping=True,
    pool_recycle=3600,
    max_overflow=20,
)


@contextmanager
def get_session(autocommit=False) -> Iterator[Session]:
    session = Session(engine, autoflush=False)
    try:
        yield session
        if autocommit:
            session.commit()
    except Exception:
        session.rollback()
        raise
    else:
        session.close()
