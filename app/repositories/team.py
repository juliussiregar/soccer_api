from typing import List, Optional
from sqlalchemy.orm import Query
from app.core.database import get_session
from app.models.team import Team
from app.utils.date import get_now

class TeamRepository:
    def create(self, payload: dict) -> Team:
        with get_session() as db:
            team = Team(**payload)
            db.add(team)
            db.commit()
            db.refresh(team)
            return team

    def find_by_id(self, team_id: int) -> Optional[Team]:
        with get_session() as db:
            return db.query(Team).filter(Team.id == team_id, Team.deleted_at.is_(None)).one_or_none()

    def update(self, team_id: int, payload: dict) -> Optional[Team]:
        with get_session() as db:
            team = db.query(Team).filter(Team.id == team_id, Team.deleted_at.is_(None)).first()
            if not team:
                return None

            # Update hanya kolom yang ada dalam payload
            for key, value in payload.items():
                if value is not None:  # Hanya update kolom dengan nilai bukan None
                    setattr(team, key, value)

            team.updated_at = get_now()  # Set waktu update terakhir
            db.commit()
            db.refresh(team)
            return team


    def delete(self, team_id: int) -> bool:
        with get_session() as db:
            team = db.query(Team).filter(Team.id == team_id, Team.deleted_at.is_(None)).first()
            if not team:
                return False

            team.deleted_at = get_now()
            db.commit()
            return True

    def list(self, limit: int = 20, page: int = 1, search: Optional[str] = None) -> List[Team]:
        with get_session() as db:
            query = db.query(Team).filter(Team.deleted_at.is_(None))

            if search:
                query = query.filter(Team.team_name.ilike(f"%{search}%"))

            query = query.order_by(Team.created_at.desc())
            offset = (page - 1) * limit
            return query.limit(limit).offset(offset).all()

    def count(self, search: Optional[str] = None) -> int:
        with get_session() as db:
            query = db.query(Team).filter(Team.deleted_at.is_(None))
            if search:
                query = query.filter(Team.team_name.ilike(f"%{search}%"))
            return query.count()
