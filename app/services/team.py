from typing import Optional
from app.models.team_official import TeamOfficial
from app.repositories.team import TeamRepository
from app.models.team import Team


class TeamService:
    def __init__(self) -> None:
        self.team_repo = TeamRepository()

    def create(self, payload: dict, official_id: int) -> Team:
        return self.team_repo.create(payload, official_id)

    def find_by_id(self, team_id: int) -> Team:
        team = self.team_repo.find_by_id(team_id)
        if not team:
            raise Exception("Team not found")
        return team

    def find_by_official_id(self, official_id: int) -> Optional[Team]:
        return self.team_repo.find_by_official_id(official_id)

    def update(self, team_id: int, payload: dict) -> Team:
        team = self.team_repo.update(team_id, payload)
        if not team:
            raise Exception("Failed to update team")
        return team

    def delete(self, team_id: int) -> bool:
        if not self.team_repo.delete(team_id):
            raise Exception("Failed to delete team")
        return True
    
    def assign_official(self, team_id: int, official_id: int) -> TeamOfficial:
        return self.team_official_repo.assign_official(team_id, official_id)

    def unassign_official(self, team_id: int, official_id: int) -> bool:
        return self.team_official_repo.unassign_official(team_id, official_id)
