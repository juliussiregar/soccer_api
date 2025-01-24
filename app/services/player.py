from typing import Optional, List, Tuple
from app.repositories.player import PlayerRepository
from app.models.player import Player


class PlayerService:
    def __init__(self) -> None:
        self.player_repo = PlayerRepository()

    def create(self, payload: dict) -> Player:
        return self.player_repo.create(payload)

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
