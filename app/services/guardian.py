from typing import List, Optional, Tuple
from app.repositories.guardian import GuardianRepository
from app.models.guardian import Guardian

class GuardianService:
    def __init__(self) -> None:
        self.guardian_repo = GuardianRepository()

    def create(self, payload: dict) -> Guardian:
        return self.guardian_repo.create(payload)

    def find_by_user_id(self, user_id: int) -> Guardian:
        guardian = self.guardian_repo.find_by_user_id(user_id)
        if not guardian:
            raise Exception("Guardian profile not found")
        return guardian

    def update(self, user_id: int, payload: dict) -> Guardian:
        guardian = self.guardian_repo.update(user_id, payload)
        if not guardian:
            raise Exception("Failed to update guardian profile")
        return guardian

    def delete(self, user_id: int) -> bool:
        if not self.guardian_repo.delete(user_id):
            raise Exception("Failed to delete guardian profile")
        return True

    def list(self, limit: int, page: int) -> Tuple[List[Guardian], int]:
        offset = (page - 1) * limit
        guardians = self.guardian_repo.list(limit, offset)
        total = self.guardian_repo.count()
        return guardians, total
    
    def list_all(self, limit: int, page: int, search: Optional[str] = None) -> Tuple[List[Guardian], int]:
        offset = (page - 1) * limit
        guardians = self.guardian_repo.list_all(limit, offset, search)
        total = self.guardian_repo.count()  # Total tanpa filter, jika ingin total filtered tambahkan logika di repository
        return guardians, total
