from fastapi import APIRouter, Depends
from typing import Optional, Annotated

from app.schemas.user_mgt import UserFilter, RekanRegister, RegisterUpdate
from app.middleware.jwt import jwt_middleware, AuthUser
from app.core.constants.auth import ROLE_ADMIN

from app.services.auth import AuthService
from app.services.user import UserService

router = APIRouter()
auth_service = AuthService()
user_service = UserService()




@router.post("/register")
def user_create(
    auth_user: Annotated[AuthUser, Depends(jwt_middleware)], body: RekanRegister
):
    auth_service.has_role(auth_user.id, ROLE_ADMIN)

    user = user_service.register(body)

    return {
        "data": {
            "id": user.id,
            "full_name": user.full_name,
            "username": user.username,
            "roles": [body.role],
            "created_at": user.created_at,
            "updated_at": user.updated_at,
        },
    }


@router.put("/change_password/{id}")
def user_update(
    auth_user: Annotated[AuthUser, Depends(jwt_middleware)], id: int, body: RegisterUpdate
):
    auth_service.has_role(auth_user.id, ROLE_ADMIN)

    user = user_service.update_password(id, body)

    return {
        "data": {
            "id": user.id,
            "full_name": user.full_name,
            "username": user.username,
            "created_at": user.created_at,
            "updated_at": user.updated_at,
        },
    }
