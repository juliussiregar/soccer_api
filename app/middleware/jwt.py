from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError, ExpiredSignatureError
from datetime import datetime, timezone
import logging

from app.schemas.user_mgt import AuthUser
from app.core.config import settings
from app.repositories.token import TokenRepository
from app.repositories.user import UserRepository

logging.basicConfig(level=logging.INFO)

oauth2_bearer = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


class JwtMiddleware:
    def __init__(self, secret_key=settings.jwt_secret, algorithm=settings.jwt_algorithm):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.user_repo = UserRepository(user_repo=self, role_repo=None)  # Memanggil repository user

    def __call__(self, token: str = Depends(oauth2_bearer)) -> AuthUser:
        token_repo = TokenRepository()

        # Check if the token is revoked
        if token_repo.is_token_revoked(token):
            raise HTTPException(status_code=401, detail="Token has been revoked")

        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            logging.info(f"Token payload: {payload}")

            user_id = payload.get("id")
            if not user_id:
                raise HTTPException(status_code=401, detail="Invalid token")

            # Ambil user dari repository dengan relasi guardian, official, dan player
            user = self.user_repo.find_by_id_with_roles_and_profiles(user_id)
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            
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

            auth_user = AuthUser(
                id=user.id,
                full_name=user.full_name,
                email=user.email,
                created_at=user.created_at,
                updated_at=user.updated_at,
                deleted_at=user.deleted_at,
                roles=[role.name for role in user.roles],
                guardian_id=user.guardian_profile.id if user.guardian_profile else None,
                official_id=user.official_profile.id if user.official_profile else None,
                player_id=user.player_profile.id if user.player_profile else None,
                team_id=team_id,   
                team_name=team_name  
            )
            return auth_user

        except ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token expired")
        except JWTError:
            raise HTTPException(status_code=401, detail="Could not validate token")
        except Exception as e:
            logging.error(f"Error in JwtMiddleware: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")


jwt_middleware = JwtMiddleware()
