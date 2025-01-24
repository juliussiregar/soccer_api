from typing import List, Tuple
from app.repositories.official import OfficialRepository
from app.models.official import Official


class OfficialService:
    def __init__(self) -> None:
        self.official_repo = OfficialRepository()

    def create(self, payload: dict) -> Official:
        return self.official_repo.create(payload)

    def find_by_user_id(self, user_id: int) -> Official:
        official = self.official_repo.find_by_user_id(user_id)
        if not official:
            raise Exception("Official profile not found")
        return official

    def update(self, user_id: int, payload: dict) -> Official:
        official = self.official_repo.update(user_id, payload)
        if not official:
            raise Exception("Failed to update official profile")
        return official

    def delete(self, user_id: int) -> bool:
        if not self.official_repo.delete(user_id):
            raise Exception("Failed to delete official profile")
        return True

    def list(self, limit: int, page: int) -> Tuple[List[Official], int]:
        offset = (page - 1) * limit
        officials = self.official_repo.list(limit, offset)
        total = self.official_repo.count()
        return officials, total
