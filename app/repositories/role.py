from typing import List
from app.core.database import get_session
from app.models.role import Role


class RoleRepository:
    def get_by_user_id(self, user_id: int) -> List[Role]:
        with get_session() as db:
            return (
                db.query(Role).join(Role.users).filter(Role.users.any(id=user_id)).all()
            )

    def find_by_name(self, name: str) -> Role | None:
        with get_session() as db:
            return db.query(Role).filter(Role.name == name).one_or_none()

    def is_name_exists(self, name: str) -> bool:
        with get_session() as db:
            name_count = db.query(Role).filter(Role.name == name).count()

        return name_count > 0

    def get_all(self) -> List[Role]:
        with get_session() as db:
            return db.query(Role).order_by(Role.name.asc()).all()
