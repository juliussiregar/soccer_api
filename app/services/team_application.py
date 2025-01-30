from typing import List
from app.core.database import get_session
from app.repositories.team_application import TeamApplicationRepository
from app.models.team_application import TeamApplication, ApplicationStatus
from app.models.team import Team
from app.repositories.team import TeamRepository


class TeamApplicationService:
    def __init__(self) -> None:
        self.application_repo = TeamApplicationRepository()
        self.team_repo = TeamRepository()

    def create(self, payload: dict) -> TeamApplication:
        return self.application_repo.create(payload)

    def find_by_id(self, application_id: int) -> TeamApplication:
        application = self.application_repo.find_by_id(application_id)
        if not application:
            raise Exception("Application not found")
        return application

    def find_by_player_id(self, player_id: int) -> List[TeamApplication]:
        return self.application_repo.find_by_player_id(player_id)

    def update_status(self, application_id: int, status: ApplicationStatus) -> TeamApplication:
        application = self.application_repo.update_status(application_id, status)
        if not application:
            raise Exception("Failed to update application status")

        # Jika status adalah ACCEPTED, tambahkan player ke tim dan tingkatkan total_players
        if status == ApplicationStatus.ACCEPTED:
            self.team_repo.increment_total_players(application.team_id)

        return application

    def delete(self, application_id: int) -> bool:
        if not self.application_repo.delete(application_id):
            raise Exception("Failed to delete application")
        return True
    
    def find_by_player_ids(self, player_ids: List[int]) -> List[TeamApplication]:
        if not player_ids:
            return []
        return self.application_repo.find_by_player_ids(player_ids)


    def get_applications_by_user_id(self, user_id: int) -> List[TeamApplication]:
        # Cari team_id berdasarkan user_id
        team_id = self.application_repo.find_team_id_by_user_id(user_id)

        # Cari aplikasi berdasarkan team_id
        return self.application_repo.find_by_team_id(team_id)

