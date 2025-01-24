from typing import Optional, List
from sqlalchemy.orm import Query
from app.core.database import get_session
from app.models.official import Official
from app.utils.date import get_now


class OfficialRepository:
    def create(self, payload: dict) -> Official:
        with get_session() as db:
            official = Official(**payload)
            db.add(official)
            db.commit()
            db.refresh(official)
            return official

    def find_by_user_id(self, user_id: int) -> Optional[Official]:
        with get_session() as db:
            return db.query(Official).filter(Official.user_id == user_id).one_or_none()

    def update(self, user_id: int, payload: dict) -> Optional[Official]:
        with get_session() as db:
            official = db.query(Official).filter(Official.user_id == user_id).first()
            if not official:
                return None

            for key, value in payload.items():
                if value is not None:
                    setattr(official, key, value)

            official.updated_at = get_now()
            db.commit()
            db.refresh(official)
            return official

    def delete(self, user_id: int) -> bool:
        with get_session() as db:
            official = db.query(Official).filter(Official.user_id == user_id).first()
            if not official:
                return False

            db.delete(official)
            db.commit()
            return True

    def list(self, limit: int, offset: int) -> List[Official]:
        with get_session() as db:
            return db.query(Official).offset(offset).limit(limit).all()

    def count(self) -> int:
        with get_session() as db:
            return db.query(Official).count()
