from typing import Optional
from app.core.database import get_session
from app.models.team import Team
from app.models.team_official import TeamOfficial
from app.utils.date import get_now


class TeamRepository:
    def create(self, payload: dict, official_id: int) -> Team:
        with get_session() as db:
            team = Team(**payload)
            db.add(team)
            db.commit()
            db.refresh(team)

            # Buat entri di tabel TeamOfficial
            team_official = TeamOfficial(team_id=team.id, official_id=official_id)
            db.add(team_official)
            db.commit()

            return team

    def find_by_id(self, team_id: int) -> Optional[Team]:
        with get_session() as db:
            return db.query(Team).filter(Team.id == team_id).one_or_none()

    def find_by_official_id(self, official_id: int) -> Optional[Team]:
        with get_session() as db:
            return db.query(Team).join(TeamOfficial).filter(TeamOfficial.official_id == official_id).one_or_none()

    def update(self, team_id: int, payload: dict) -> Optional[Team]:
        with get_session() as db:
            team = db.query(Team).filter(Team.id == team_id).first()
            if not team:
                return None

            for key, value in payload.items():
                if value is not None:
                    setattr(team, key, value)

            team.updated_at = get_now()
            db.commit()
            db.refresh(team)
            return team


