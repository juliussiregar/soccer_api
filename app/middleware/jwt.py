from app.core.config import settings
from fastapi.security import HTTPAuthorizationCredentials, OAuth2PasswordBearer
from fastapi import Depends, HTTPException
from jose import jwt, JWTError, ExpiredSignatureError
from pydantic import BaseModel

oauth2_bearer = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")


class AuthUser(BaseModel):
    id: int


class JwtMiddleware:
    def __init__(
        self, secret_key=settings.jwt_secret, algorithm=settings.jwt_algorithm
    ):
        self.secret_key = secret_key
        self.algorithm = algorithm

    def __call__(
        self, credentials: HTTPAuthorizationCredentials = Depends(oauth2_bearer)
    ):
        if not credentials:
            raise HTTPException(401, "Unauthorized")

        token = credentials

        try:
            payload = jwt.decode(token, self.secret_key, algorithms=self.algorithm)
            user_id: str = payload.get("id")
            if user_id is None:
                raise HTTPException(401, "invalid token")

            user = AuthUser(id=user_id)
            return user
        except ExpiredSignatureError:
            raise HTTPException(401, "Token expired")
        except JWTError:
            raise HTTPException(401, "Could not validate token")
        except Exception:
            raise HTTPException(500, "Internal server error")


jwt_middleware = JwtMiddleware()