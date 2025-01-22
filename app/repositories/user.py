from typing import List, Tuple
from passlib.context import CryptContext
from sqlalchemy.orm import Query, joinedload
from sqlalchemy import insert, delete

from app.core.database import get_session
from app.models.user import User
from app.repositories.role import RoleRepository
from app.utils.date import get_now
from app.models.role import Role, user_role_association

from app.schemas.user_mgt import UserCreate, UserUpdate, UserFilter, RegisterUpdate,PasswordUpdate

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserRepository:
    def __init__(self, user_repo: 'UserRepository', role_repo: 'RoleRepository') -> None:
        self.user_repo = user_repo
        self.role_repo = role_repo

    def find_by_id(self, id: int) -> User | None:
        with get_session() as db:
            return (
                db.query(User)
                .filter(User.id == id, User.deleted_at.is_(None))
                .one_or_none()
            )

    def find_by_username(self, username: str) -> User | None:
        with get_session() as db:
            return (
                db.query(User)
                .filter(User.username == username, User.deleted_at.is_(None))
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
        if user is None:
            return False

        if len(user.roles) == 0:
            return False

        for role in user.roles:
            if role.name == role_name:
                return True

        return False

    def filtered(self, query: Query, filter: UserFilter) -> Query:
        if filter.search is not None:
            query = query.filter(User.username == filter.search)
            # TODO: Add other columns to search

        return query


    # def get_all_filtered(self, filter: UserFilter) -> List[User]:
    #     with get_session() as db:
    #         query = db.query(User).join(User.company).options(joinedload(User.company))

    #         # Filter based on the provided filters
    #         query = self.filtered(query, filter)

    #         # Include users with null deleted_at
    #         query = query.filter(User.deleted_at.is_(None))

    #         query = query.order_by(User.created_at.desc())

    #         if filter.limit is not None:
    #             query = query.limit(filter.limit)

    #         if filter.page is not None and filter.limit is not None:
    #             offset = (filter.page - 1) * filter.limit
    #             query = query.offset(offset)

    #         return query.options(joinedload(User.roles)).all()



    def count_by_filter(self, filter: UserFilter) -> int:
        with get_session() as db:
            query = db.query(User)

            # Filter based on the provided filters
            query = self.filtered(query, filter)

            # Include users with null deleted_at
            query = query.filter(User.deleted_at.is_(None))

            return query.count()

    def password_hash(self, password: str) -> str:
        return bcrypt_context.hash(password)

    def insert(self, payload: UserCreate) -> User:
        user = User()
        user.username = payload.username

        user.full_name = payload.full_name
        user.email = payload.email

        hash_password = self.password_hash(payload.password)
        user.password = hash_password


        with get_session() as db:
            db.add(user)
            db.flush()

            if payload.role is not None:
                vendor_role_id = (
                    db.query(Role.id).filter(Role.name == payload.role).one()
                )
                if len(vendor_role_id) > 0:
                    role_data = [
                        {"user_id": user.id, "role_id": vendor_role_id[0]},
                    ]
                    insert_user_role = insert(user_role_association).values(role_data)
                    db.execute(insert_user_role)



            db.commit()
            db.refresh(user)

        return user

    def update(self, user_id: int, payload: UserUpdate) -> User | None:
        with get_session() as db:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return None

            # Update basic user information
            if payload.username:
                user.username = payload.username
            if payload.full_name:
                user.full_name = payload.full_name
            if payload.email:
                user.email = payload.email
            if payload.password:
                user.password = self.password_hash(payload.password)

            user.updated_at = get_now()

            # Handle role update if provided
            if payload.role:
                role = db.query(Role).filter(Role.name == payload.role).first()
                if role:
                    # Remove existing roles
                    db.execute(
                        delete(user_role_association).where(
                            user_role_association.c.user_id == user_id
                        )
                    )
                    # Add new role
                    db.execute(
                        user_role_association.insert().values(
                            user_id=user_id, role_id=role.id
                        )
                    )

            db.commit()
            db.refresh(user)
            return user

    def is_username_used(self, username: str, except_id: int = 0) -> bool:
        with get_session() as db:
            username_count = (
                db.query(User)
                .filter(User.username == username, User.id != except_id)
                .count()
            )

        return username_count > 0

    def delete(self, user_id: int) -> bool:
        with get_session() as db:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return False

            # Soft delete - update deleted_at timestamp
            user.deleted_at = get_now()

            # Remove role associations
            db.execute(
                delete(user_role_association).where(
                    user_role_association.c.user_id == user_id
                )
            )

            db.commit()
            return True

    def is_email_used(self, email: str, except_id: int = 0) -> bool:
        with get_session() as db:
            email_count = (
                db.query(User)
                .filter(User.email == email, User.id != except_id)
                .count()
            )
            return email_count > 0

    def update_password(self, id: int, payload: RegisterUpdate) -> User | None:
        user = self.find_by_id(id)
        if user is None:
            return user


        if payload.password is not None:
            hash_password = self.password_hash(payload.password)
            user.password = hash_password


        user.updated_at = get_now()

        with get_session() as db:
            db.add(user)
            db.commit()
            db.refresh(user)

        return user
    
    def update_user_password(self, id: int, payload: PasswordUpdate) -> User | None:
        user = self.find_by_id(id)
        if user is None:
            return user


        if payload.new_password is not None:
            hash_password = self.password_hash(payload.new_password)
            user.password = hash_password


        user.updated_at = get_now()

        with get_session() as db:
            db.add(user)
            db.commit()
            db.refresh(user)

        return user

