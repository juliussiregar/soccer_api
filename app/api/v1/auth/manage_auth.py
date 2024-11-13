from fastapi import APIRouter, Depends, HTTPException, Form
from app.middleware.jwt import jwt_middleware, oauth2_bearer, revoked_tokens
from app.services.auth import AuthService
from app.schemas.user_mgt import AuthUser
from typing import Annotated

router = APIRouter()
auth_service = AuthService()

@router.post("/auth/login")
def auth_get_access_token(
    username: str = Form(...),  # Menggunakan 'username' agar sesuai dengan standar OAuth2
    password: str = Form(...)
):
    access_token = auth_service.generate_token(username, password)
    if not access_token:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return {"access_token": access_token, "type": "Bearer"}

@router.get("/auth/me")
def auth_get_me(auth_user: Annotated[AuthUser, Depends(jwt_middleware)]):
    user_data = auth_service.get_user_details(auth_user.id)
    return user_data

@router.post("/auth/logout")
def logout(auth_user: Annotated[AuthUser, Depends(jwt_middleware)], token: str = Depends(oauth2_bearer)):
    if not auth_user:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    revoked_tokens.add(token)
    return {"message": "Logout successful. Token has been revoked."}
