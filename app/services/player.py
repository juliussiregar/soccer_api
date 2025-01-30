from typing import Optional, List, Tuple
from app.repositories.player import PlayerRepository
from app.repositories.guardian import GuardianRepository
from app.models.player import Player


class PlayerService:
    def __init__(self) -> None:
        self.player_repo = PlayerRepository()
        self.guardian_repo = GuardianRepository()

    def create(self, payload: dict, user_id: int) -> Player:
        # Temukan Guardian berdasarkan user_id
        guardian = self.guardian_repo.find_by_user_id(user_id)
        if not guardian:
            raise Exception(f"Guardian with user_id {user_id} not found.")

        # Buat player baru
        player = self.player_repo.create(payload)

        # Tambahkan relasi di GuardianPlayer
        self.player_repo.create_guardian_player(guardian_id=guardian.id, player_id=player.id)

        return player

    def find_by_id(self, player_id: int) -> Player:
        player = self.player_repo.find_by_id(player_id)
        if not player:
            raise Exception("Player not found")
        return player

    def find_by_guardian_id(self, guardian_id: int) -> List[Player]:
        return self.player_repo.find_by_guardian_id(guardian_id)

    def list_all(self, limit: int, page: int) -> Tuple[List[Player], int]:
        offset = (page - 1) * limit
        players = self.player_repo.list_all(limit, offset)
        total = self.player_repo.count_all()
        return players, total

    def update(self, player_id: int, payload: dict) -> Player:
        player = self.player_repo.update(player_id, payload)
        if not player:
            raise Exception("Failed to update player")
        return player

    def delete(self, player_id: int) -> bool:
        if not self.player_repo.delete(player_id):
            raise Exception("Failed to delete player")
        return True

    def find_by_team_id(self, team_id: int) -> List[Player]:
        return self.player_repo.find_by_team_id(team_id)