from typing import Optional, List
from sqlalchemy.orm import Query
from app.core.database import get_session
from app.models.guardian import Guardian
from app.utils.date import get_now

class GuardianRepository:
    def create(self, payload: dict) -> Guardian:
        with get_session() as db:
            guardian = Guardian(**payload)
            db.add(guardian)
            db.commit()
            db.refresh(guardian)
            return guardian

    def find_by_user_id(self, user_id: int) -> Optional[Guardian]:
        with get_session() as db:
            return db.query(Guardian).filter(Guardian.user_id == user_id).one_or_none()

    def update(self, user_id: int, payload: dict) -> Optional[Guardian]:
        with get_session() as db:
            guardian = db.query(Guardian).filter(Guardian.user_id == user_id).first()
            if not guardian:
                return None

            for key, value in payload.items():
                if value is not None:
                    setattr(guardian, key, value)

            guardian.updated_at = get_now()
            db.commit()
            db.refresh(guardian)
            return guardian

    def delete(self, user_id: int) -> bool:
        with get_session() as db:
            guardian = db.query(Guardian).filter(Guardian.user_id == user_id).first()
            if not guardian:
                return False

            db.delete(guardian)
            db.commit()
            return True

    def list(self, limit: int, offset: int) -> List[Guardian]:
        with get_session() as db:
            return db.query(Guardian).offset(offset).limit(limit).all()

    def count(self) -> int:
        with get_session() as db:
            return db.query(Guardian).count()
        
    def list_all(self, limit: int, offset: int, search: Optional[str] = None) -> List[Guardian]:
        with get_session() as db:
            query = db.query(Guardian)
            
            # Apply search filter
            if search:
                query = query.filter(Guardian.name.ilike(f"%{search}%"))
            
            return query.offset(offset).limit(limit).all()

