from typing import Optional, List
from app.core.database import get_session
from app.models.official import Official
from app.models.team_application import TeamApplication, ApplicationStatus
from app.models.team_official import TeamOfficial
from app.utils.date import get_now


class TeamApplicationRepository:
    def create(self, payload: dict) -> TeamApplication:
        with get_session() as db:
            application = TeamApplication(**payload)
            db.add(application)
            db.commit()
            db.refresh(application)
            return application

    def find_by_id(self, application_id: int) -> Optional[TeamApplication]:
        with get_session() as db:
            return db.query(TeamApplication).filter(TeamApplication.id == application_id).one_or_none()

    def find_by_player_id(self, player_id: int) -> List[TeamApplication]:
        with get_session() as db:
            return db.query(TeamApplication).filter(TeamApplication.player_id == player_id).all()

    def update_status(self, application_id: int, status: ApplicationStatus) -> Optional[TeamApplication]:
        with get_session() as db:
            application = db.query(TeamApplication).filter(TeamApplication.id == application_id).first()
            if not application:
                return None

            application.status = status
            application.updated_at = get_now()
            db.commit()
            db.refresh(application)
            return application

    def delete(self, application_id: int) -> bool:
        with get_session() as db:
            application = db.query(TeamApplication).filter(TeamApplication.id == application_id).first()
            if not application:
                return False

            db.delete(application)
            db.commit()
            return True
        
    def find_by_player_ids(self, player_ids: List[int]) -> List[TeamApplication]:
        with get_session() as db:
            return db.query(TeamApplication).filter(TeamApplication.player_id.in_(player_ids)).all()
        
    def find_by_team_id(self, team_id: int) -> List[TeamApplication]:
        with get_session() as db:
            return db.query(TeamApplication).filter(TeamApplication.team_id == team_id).all()

    def find_team_id_by_user_id(self, user_id: int) -> int:
        with get_session() as db:
            # Cari official berdasarkan user_id
            official = db.query(Official).filter(Official.user_id == user_id).first()
            if not official:
                raise Exception("No official found for the given user ID")

            # Cari team_id berdasarkan official_id
            team_official = db.query(TeamOfficial).filter(TeamOfficial.official_id == official.id).first()
            if not team_official:
                raise Exception("No team associated with this official")

            return team_official.team_id
