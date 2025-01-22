from typing import List
from passlib.context import CryptContext
from sqlalchemy.orm import Query, joinedload
from sqlalchemy import or_

from app.core.database import get_session
from app.models.user import User
from app.models.role import Role, user_role_association

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthRepository:
    def find_by_id(self, id: int) -> User | None:
        """Menemukan pengguna berdasarkan ID unik mereka, dengan eager loading pada `roles`."""
        with get_session() as db:
            return (
                db.query(User)
                .filter(User.id == id, User.deleted_at.is_(None))
                .options(joinedload(User.roles))  # Eager load roles di sini
                .one_or_none()
            )

    def find_by_username_or_email(self, identifier: str) -> User | None:
        with get_session() as db:
            return (
                db.query(User)
                .filter(
                    or_(User.username == identifier, User.email == identifier),
                    User.deleted_at.is_(None)
                )
                .options(joinedload(User.roles))  
                .one_or_none()
            )

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return bcrypt_context.verify(plain_password, hashed_password)

    def find_by_id_with_roles(self, id: int) -> User | None:
        with get_session() as db:
            return (
                db.query(User)
                .filter(User.id == id)
                .options(joinedload(User.roles))
                .one_or_none()
            )

    def has_role(self, id: int, role_name: str) -> bool:
        user = self.find_by_id_with_roles(id)
        if user is None or not user.roles:
            return False
        return any(role.name == role_name for role in user.roles)

    def is_username_or_email_used(self, username: str, email: str, except_id: int = 0) -> bool:
        with get_session() as db:
            username_or_email_count = (
                db.query(User)
                .filter(
                    or_(User.username == username, User.email == email),
                    User.id != except_id
                )
                .count()
            )
        return username_or_email_count > 0
