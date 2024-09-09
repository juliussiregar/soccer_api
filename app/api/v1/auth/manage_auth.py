from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated

from app.middleware.jwt import AuthUser, JwtMiddleware
from app.services.auth import AuthService
from app.services.user import UserService


router = APIRouter()
auth_service = AuthService()
user_service = UserService()


@router.post("/auth/token")
def auth_get_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    access_token = auth_service.generate_token(form_data.username, form_data.password)

    return {"access_token": access_token, "type": "Bearer"}


@router.get("/auth/me")
def auth_get_me(auth_user: Annotated[AuthUser, Depends(JwtMiddleware())]):
    
    return auth_user
