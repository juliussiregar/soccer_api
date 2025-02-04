import logging
from typing import List, Optional, Tuple
from app.utils.logger import logger
from passlib.context import CryptContext
from sqlalchemy.orm import Query, joinedload
from sqlalchemy import insert, delete

from app.core.database import get_session
from app.models.guardian_player import GuardianPlayer
from app.models.team_official import TeamOfficial
from app.models.team_player import TeamPlayer
from app.models.user import User
from app.models.guardian import Guardian
from app.models.player import Player
from app.models.official import Official
from app.repositories.role import RoleRepository
from app.utils.date import get_now
from app.models.role import Role, user_role_association

from app.schemas.user_mgt import AuthUser, RegisterGuardian, UserCreate, UserUpdate, UserFilter, RegisterUpdate,PasswordUpdate, RegisterOfficial, RegisterPlayer
from app.utils.exception import InternalErrorException

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
            
    def find_by_id_with_roles_and_profiles(self, id: int) -> User | None:
        """
        Ambil user berdasarkan ID dengan relasi ke Role, Guardian, Official, Player, serta informasi tim mereka.
        """
        with get_session() as db:
            return (
                db.query(User)
                .filter(User.id == id, User.deleted_at.is_(None))
                .options(
                    joinedload(User.roles),
                    joinedload(User.guardian_profile),
                    joinedload(User.official_profile)
                    .joinedload(Official.team_official)  # Join ke TeamOfficial
                    .joinedload(TeamOfficial.team),  # Join ke Team
                    
                    joinedload(User.player_profile)
                    .joinedload(Player.team_player)  # Join ke TeamPlayer
                    .joinedload(TeamPlayer.team)  # Join ke Team
                )
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
    # Filter pencarian berdasarkan full_name (query string `q`)
        if filter.search:
            query = query.filter(User.full_name.ilike(f"%{filter.search}%"))  
            logging.info(f"Filtered query applied with search: {filter.search}")
        return query


    def get_all_filtered(self, filter: Optional[UserFilter] = None) -> List[User]:
        with get_session() as db:
            query = db.query(User)

            # Include users with null deleted_at
            query = query.filter(User.deleted_at.is_(None))

            # Order by creation date
            query = query.order_by(User.created_at.desc())

            # Default pagination settings
            default_limit = 20
            default_page = 1

            # Apply limit and offset based on filter or default values
            limit = default_limit
            page = default_page

            if filter is not None:
                limit = filter.limit if filter.limit is not None else default_limit
                page = filter.page if filter.page is not None else default_page

            query = query.limit(limit)
            offset = (page - 1) * limit
            query = query.offset(offset)

            return query.options(joinedload(User.roles)).all()




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
            # Ambil user dari database
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return None

            # Update basic user information
            if payload.full_name:
                user.full_name = payload.full_name
            if payload.email:
                user.email = payload.email
            if payload.password:
                user.password = self.password_hash(payload.password)

            user.updated_at = get_now()

            # Handle role update if provided
            if payload.role:
                # Cari role berdasarkan nama
                role = db.query(Role).filter(Role.name == payload.role).first()

                # Jika role tidak ditemukan, buat role baru
                if not role:
                    role = Role(name=payload.role)
                    db.add(role)
                    db.commit()
                    db.refresh(role)  # Refresh untuk mendapatkan ID role baru

                # Hapus semua role lama yang terkait dengan user
                db.execute(
                    delete(user_role_association).where(
                        user_role_association.c.user_id == user_id
                    )
                )

                # Tambahkan role baru ke user
                db.execute(
                    user_role_association.insert().values(
                        user_id=user_id, role_id=role.id
                    )
                )

            # Commit semua perubahan dan refresh objek user
            db.commit()
            db.refresh(user)
            return user
        

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

    def insert_guardian(self, payload: RegisterGuardian) -> User:
        """Membuat user sekaligus menjadi Guardian dengan rollback jika terjadi kesalahan"""

        user = User(
            full_name=payload.full_name,
            email=payload.email,
            password=self.password_hash(payload.password),
        )

        with get_session() as db:
            try:
                db.add(user)
                db.flush()  # Flush untuk mendapatkan `user.id`

                # Tambahkan Guardian
                guardian = Guardian(
                    user_id=user.id,
                    name=payload.full_name,
                    birth_date=payload.birth_date,
                    kartu_keluarga=payload.kartu_keluarga,
                    ktp=payload.ktp,
                    phone_number=payload.phone_number,
                    address=payload.address,
                )
                db.add(guardian)

                # Tambahkan role "GUARDIAN" secara otomatis
                role = db.query(Role).filter(Role.name == "GUARDIAN").first()
                if role:
                    db.execute(
                        user_role_association.insert().values(user_id=user.id, role_id=role.id)
                    )

                db.commit()
                db.refresh(user)  # Refresh user agar datanya terbaru
                return user

            except Exception as e:
                db.rollback()  # Rollback semua perubahan jika ada error
                logger.error(f"Error inserting guardian: {str(e)}")
                raise InternalErrorException("Failed to register guardian")

    
    def insert_official(self, payload: RegisterOfficial) -> User:
        """Membuat user sekaligus menjadi Official"""

        user = User(
            full_name=payload.full_name,
            email=payload.email,
            password=self.password_hash(payload.password),
        )

        with get_session() as db:
            try:
                db.add(user)
                db.flush()  # Flush untuk mendapatkan `user.id`

                # Tambahkan Offial
                official = Official(
                    user_id=user.id,
                    name=payload.full_name,
                    position=payload.position,
                    profile_picture=payload.profile_picture,
                )
                db.add(official)

                # Tambahkan role "OFFICIAL" secara otomatis
                role = db.query(Role).filter(Role.name == "OFFICIAL").first()
                if role:
                    db.execute(
                        user_role_association.insert().values(user_id=user.id, role_id=role.id)
                    )

                db.commit()
                db.refresh(user)  # Refresh user agar datanya terbaru

                return user
            except Exception as e:
                db.rollback()  # Rollback semua perubahan jika ada error
                logger.error(f"Error inserting guardian: {str(e)}")
                raise InternalErrorException("Failed to register guardian")
    
    def insert_player(self, payload: RegisterPlayer, auth_user: AuthUser) -> User:
        """Membuat user sekaligus menjadi Player yang terhubung ke Guardian (ID dari token)"""

        user = User(
            full_name=payload.full_name,
            email=payload.email,
            password=self.password_hash(payload.password),
        )

        with get_session() as db:
            try:
                db.add(user)
                db.flush()  # Flush untuk mendapatkan `user.id`

                # Tambahkan Player dengan atribut lengkap
                player = Player(
                    user_id=user.id,
                    name=payload.full_name,
                    birth_date=payload.birth_date,
                    main_position=payload.main_position,
                    second_position=payload.second_position,
                    third_position=payload.third_position,
                    profile_picture=payload.profile_picture,
                    jersey_number=payload.jersey_number,
                    NISN=payload.NISN,
                    dominant_foot=payload.dominant_foot,
                    height=payload.height,
                    weight=payload.weight,
                    bio=payload.bio,
                )
                db.add(player)
                db.flush()  # Flush agar `player.id` tersedia sebelum digunakan di `GuardianPlayer`

                # Tambahkan GuardianPlayer (hubungan antara Guardian & Player)
                guardian_player = GuardianPlayer(
                    guardian_id=auth_user.guardian_id,  # Mengambil Guardian ID dari token
                    player_id=player.id,
                    relationship_guardian=payload.relationship_guardian,
                )
                db.add(guardian_player)

                # Tambahkan role "PLAYER" secara otomatis
                role = db.query(Role).filter(Role.name == "PLAYER").first()
                if role:
                    db.execute(
                        user_role_association.insert().values(user_id=user.id, role_id=role.id)
                    )

                db.commit()
                db.refresh(user)  # Refresh user agar datanya terbaru

                return user

            except Exception as e:
                db.rollback()  # Rollback semua perubahan jika ada error
                logger.error(f"Error inserting guardian: {str(e)}")
                raise InternalErrorException("Failed to register guardian")
