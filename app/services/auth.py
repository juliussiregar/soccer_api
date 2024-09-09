from datetime import datetime, timedelta
from jose import jwt

from app.repositories.user import UserRepository
from app.core.constants.auth import JWT_TOKEN_EXPIRE_IN_MIN
from app.utils.exception import UnauthorizedException
from app.core.config import settings

from app.core.constants.auth import ROLE_ADMIN


class AuthService:
    def __init__(self) -> None:
        self.user_repo = UserRepository()

    def generate_token(self, username: str, password: str) -> str:
        user = self.user_repo.find_by_username(username)

        if user is None:
            raise UnauthorizedException("invalid credentials")

        pass_is_valid = self.user_repo.verify_password(password, user.password)
        if not pass_is_valid:
            raise UnauthorizedException("invalid credentials")

        expire = datetime.utcnow() + timedelta(minutes=JWT_TOKEN_EXPIRE_IN_MIN)
        encode = {"sub": user.username, "id": user.id, "exp": expire}

        access_token = jwt.encode(
            encode, settings.jwt_secret, algorithm=settings.jwt_algorithm
        )

        return access_token

    def has_role(self, user_id: int, role_name: str) -> None:
        if not self.user_repo.has_role(user_id, role_name):
            if not self.user_repo.has_role(user_id, ROLE_ADMIN):
                raise UnauthorizedException(f"only {role_name} can perform this action")


    def user_exists(self, user_id: int) -> None:
        if self.user_repo.find_by_id(user_id) is None:
            raise UnauthorizedException(f"User id: {user_id} Not found")
            
    # def has_role_peserta (self, user_id : int, role_name: str) -> None:
    #     if not self.user_repo.has_role (user_id, role_name):
    #         raise UnauthorizedException(f"only {role_name} can perform this action")