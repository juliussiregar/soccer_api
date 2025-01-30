from typing import List
from app.core.database import get_session
from app.models.team_application import TeamApplication, ApplicationStatus
from app.models.team import Team
from app.repositories.team_application import TeamApplicationRepository
from app.repositories.team import TeamRepository
from app.repositories.player import PlayerRepository  



class TeamApplicationService:
    def __init__(self) -> None:
        self.application_repo = TeamApplicationRepository()
        self.team_repo = TeamRepository()
        self.player_repo = PlayerRepository() 


    def create(self, payload: dict) -> TeamApplication:
        return self.application_repo.create(payload)

    def find_by_id(self, application_id: int) -> TeamApplication:
        application = self.application_repo.find_by_id(application_id)
        if not application:
            raise Exception("Application not found")
        return application

    def find_by_player_id(self, player_id: int) -> List[TeamApplication]:
        return self.application_repo.find_by_player_id(player_id)

    def find_by_player_ids(self, player_ids: List[int]) -> List[TeamApplication]:
        if not player_ids:
            return []
        return self.application_repo.find_by_player_ids(player_ids)

    def delete(self, application_id: int) -> bool:
        if not self.application_repo.delete(application_id):
            raise Exception("Failed to delete application")
        return True

    def get_applications_by_user_id(self, user_id: int) -> List[TeamApplication]:
        team_id = self.application_repo.find_team_id_by_user_id(user_id)
        return self.application_repo.find_by_team_id(team_id)

    def update_status(self, application_id: int, status: ApplicationStatus) -> TeamApplication:
        application = self.application_repo.find_by_id(application_id)
        if not application:
            raise Exception("Application not found")

        updated_application = self.application_repo.update_status(application_id, status)

        if not updated_application:
            raise Exception("Failed to update application status")

        return updated_application


    def delete(self, application_id: int) -> bool:
        if not self.application_repo.delete(application_id):
            raise Exception("Failed to delete application")
        return True
    
    def find_by_player_ids(self, player_ids: List[int]) -> List[TeamApplication]:
        if not player_ids:
            return []
        return self.application_repo.find_by_player_ids(player_ids)

    def get_applications_by_user_id(self, user_id: int):
        team_id = self.application_repo.find_team_id_by_user_id(user_id)

        if not team_id:
            return []

        applications = self.application_repo.find_by_team_id(team_id)
        player_ids = [app.player_id for app in applications]

        players = {player.id: player.name for player in self.player_repo.find_by_ids(player_ids)}

        for app in applications:
            app.name = players.get(app.player_id, "Unknown")

        return applications





