from typing import List
from passlib.context import CryptContext
from sqlalchemy.orm import Query, joinedload
from sqlalchemy import or_

from app.core.database import get_session
from app.models.official import Official
from app.models.player import Player
from app.models.team_official import TeamOfficial
from app.models.team_player import TeamPlayer
from app.models.user import User
from app.models.role import Role, user_role_association

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthRepository:
    def find_by_id_with_profiles(self, user_id: int) -> User | None:
        """
        Mengambil user berdasarkan ID dengan semua profil terkait (Guardian, Official, Player)
        serta informasi tim jika mereka adalah Official atau Player.
        """
        with get_session() as db:
            user = (
                db.query(User)
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
                .filter(User.id == user_id)
                .one_or_none()
            )

            if not user:
                return None

            # Inisialisasi team_id dan team_name
            team_id = None
            team_name = None

            # Jika user adalah Official, cek apakah dia memiliki tim
            if user.official_profile and user.official_profile.team_official:
                team = user.official_profile.team_official.team
                if team:
                    team_id = team.id
                    team_name = team.team_name

            # Jika user adalah Player, cek apakah dia memiliki tim
            if user.player_profile and user.player_profile.team_player:
                team = user.player_profile.team_player.team
                if team:
                    team_id = team.id
                    team_name = team.team_name

            # Tambahkan informasi tim ke user sebelum return
            user.team_id = team_id
            user.team_name = team_name

            return user


    def find_by_email(self, identifier: str) -> User | None:
        with get_session() as db:
            return (
                db.query(User)
                .filter(
                    or_(User.email == identifier),
                    User.deleted_at.is_(None)
                )
                .options(joinedload(User.roles))  
                .one_or_none()
            )
            
    def find_by_email_with_profiles(self, email: str) -> User | None:
        """
        Mengambil user berdasarkan email dengan semua profil terkait (Guardian, Official, Player)
        serta informasi tim jika mereka adalah Official atau Player.
        """
        with get_session() as db:
            user = (
                db.query(User)
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
                .filter(User.email == email)
                .one_or_none()
            )

            if not user:
                return None

            # Inisialisasi team_id dan team_name
            team_id = None
            team_name = None

            # Jika user adalah Official, cek apakah dia memiliki tim
            if user.official_profile and user.official_profile.team_official:
                team = user.official_profile.team_official.team
                if team:
                    team_id = team.id
                    team_name = team.team_name

            # Jika user adalah Player, cek apakah dia memiliki tim
            if user.player_profile and user.player_profile.team_player:
                team = user.player_profile.team_player.team
                if team:
                    team_id = team.id
                    team_name = team.team_name

            # Tambahkan informasi tim ke user sebelum return
            user.team_id = team_id
            user.team_name = team_name

            return user

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

    def is_email_used(self, email: str, except_id: int = 0) -> bool:
        with get_session() as db:
            email_count = (
                db.query(User)
                .filter(
                    or_(User.email == email),
                    User.id != except_id
                )
                .count()
            )
        return email_count > 0
