
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Annotated
from app.middleware.jwt import jwt_middleware, oauth2_bearer, revoked_tokens  # Import oauth2_bearer and revoked_tokens
from app.services.auth import AuthService
from app.schemas.user_mgt import AuthUser

router = APIRouter()
auth_service = AuthService()

class LoginRequest(BaseModel):
    identifier: str  # Username or email
    password: str

@router.post("/auth/login")
def auth_get_access_token(login_data: LoginRequest):
    access_token = auth_service.generate_token(login_data.identifier, login_data.password)
    if not access_token:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return {"access_token": access_token, "type": "Bearer"}

@router.get("/auth/me")
def auth_get_me(auth_user: Annotated[AuthUser, Depends(jwt_middleware)]):
    user_data = auth_service.get_user_details(auth_user.id)
    return user_data

@router.post("/auth/logout")
def logout(auth_user: Annotated[AuthUser, Depends(jwt_middleware)], token: str = Depends(oauth2_bearer)):
    """
    Endpoint untuk logout. Token akan dicabut dengan menambahkannya ke revoked_tokens.
    """
    if not auth_user:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    revoked_tokens.add(token)

    return {"message": "Logout successful. Token has been revoked."}
