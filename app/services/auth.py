from datetime import datetime, timedelta
from jose import jwt
from app.repositories.auth import AuthRepository
from app.utils.exception import UnauthorizedException
from app.core.constants.auth import JWT_TOKEN_EXPIRE_IN_MIN
from app.core.config import settings
from app.schemas.user_mgt import AuthUser
import logging
from sqlalchemy.orm import joinedload


class AuthService:
    def __init__(self) -> None:
        self.auth_repo = AuthRepository()

    def generate_token(self, identifier: str, password: str) -> str:
        # Ambil user berdasarkan email dengan semua profil terkait (Guardian, Official, Player) dan informasi tim
        user = self.auth_repo.find_by_email_with_profiles(identifier)
        
        if user is None or not self.auth_repo.verify_password(password, user.password):
            raise UnauthorizedException("Invalid credentials")

        expire = datetime.utcnow() + timedelta(minutes=JWT_TOKEN_EXPIRE_IN_MIN)

        # Inisialisasi nilai default untuk team_id dan team_name
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

        # Tambahkan informasi guardian, official, player, dan tim ke dalam token
        encode = {
            "id": user.id,
            "full_name": user.full_name,
            "email": user.email,
            "roles": [role.name for role in user.roles],
            "guardian_id": user.guardian_profile.id if user.guardian_profile else None,
            "official_id": user.official_profile.id if user.official_profile else None,
            "player_id": user.player_profile.id if user.player_profile else None,
            "team_id": team_id,  # ✅ Tambahkan team_id jika ada
            "team_name": team_name,  # ✅ Tambahkan team_name jika ada
            "exp": expire
        }

        return jwt.encode(encode, settings.jwt_secret, algorithm=settings.jwt_algorithm)



    def get_user_details(self, user_id: int) -> AuthUser:
        try:
            # Gunakan find_by_id_with_profiles untuk memuat semua relasi
            user = self.auth_repo.find_by_id_with_profiles(user_id)

            if user is None:
                raise UnauthorizedException("User not found")

            # Inisialisasi nilai default untuk team_id dan team_name
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

            # Buat objek AuthUser dengan informasi lengkap
            user_data = AuthUser(
                id=user.id,
                full_name=user.full_name,
                email=user.email,
                created_at=user.created_at,
                updated_at=user.updated_at,
                deleted_at=user.deleted_at,
                roles=[role.name for role in user.roles],  # ✅ Pastikan roles dimuat
                guardian_id=user.guardian_profile.id if user.guardian_profile else None,
                official_id=user.official_profile.id if user.official_profile else None,
                player_id=user.player_profile.id if user.player_profile else None,
                team_id=team_id,  # ✅ Tambahkan team_id jika ada
                team_name=team_name,  # ✅ Tambahkan team_name jika ada
            )
            return user_data

        except Exception as e:
            logging.error(f"Error in get_user_details: {e}")
            raise UnauthorizedException("Failed to retrieve user details")
