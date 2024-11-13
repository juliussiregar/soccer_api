#middleware/jwt.py
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError, ExpiredSignatureError
from app.schemas.user_mgt import AuthUser
from app.core.config import settings
from datetime import datetime, timezone
import logging

logging.basicConfig(level=logging.INFO)

oauth2_bearer = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

revoked_tokens = set()

class JwtMiddleware:
    def __init__(self, secret_key=settings.jwt_secret, algorithm=settings.jwt_algorithm):
        self.secret_key = secret_key
        self.algorithm = algorithm

    def __call__(self, token: str = Depends(oauth2_bearer)) -> AuthUser:
        if token in revoked_tokens:
            raise HTTPException(status_code=401, detail="Token has been revoked")

        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            logging.info(f"Token payload: {payload}")

            auth_user = AuthUser(
                id=payload.get("id"),
                company_id=payload.get("company_id"),
                full_name=payload.get("full_name"),
                username=payload.get("username", ""),
                email=payload.get("email", ""),
                created_at=payload.get("created_at", datetime.now(timezone.utc)),
                updated_at=payload.get("updated_at"),
                deleted_at=payload.get("deleted_at"),
                created_by=payload.get("created_by"),
                roles=payload.get("roles", [])  
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
