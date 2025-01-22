from typing import List, Optional, Tuple
from app.models.team import Team
from app.repositories.team import TeamRepository

class TeamService:
    def __init__(self) -> None:
        self.team_repo = TeamRepository()

    def create(self, payload: dict) -> Team:
        return self.team_repo.create(payload)

    def find_by_id(self, team_id: int) -> Team:
        team = self.team_repo.find_by_id(team_id)
        if not team:
            raise Exception("Team not found")
        return team

    def update(self, team_id: int, payload: dict) -> Team:
        team = self.team_repo.update(team_id, payload)
        if not team:
            raise Exception("Failed to update team or team not found")
        return team

    def delete(self, team_id: int) -> bool:
        if not self.team_repo.delete(team_id):
            raise Exception("Failed to delete team or team not found")
        return True

    def list(self, limit: int = 20, page: int = 1, search: Optional[str] = None) -> Tuple[List[Team], int, int]:
        teams = self.team_repo.list(limit, page, search)
        total_rows = self.team_repo.count(search)
        total_pages = (total_rows + limit - 1) // limit
        return teams, total_rows, total_pages
    


