from fastapi import APIRouter, Depends, HTTPException
from typing import Optional, Annotated

from app.schemas.user_mgt import UserCreate, UserUpdate, RegisterUpdate

from app.middleware.jwt import jwt_middleware, AuthUser
from app.core.constants.auth import ROLE_ADMIN

from app.services.auth import AuthService
from app.services.user import UserService

router = APIRouter()
auth_service = AuthService()
user_service = UserService()


@router.get("/user", description="For user management")
def user_list(
    auth_user: Annotated[AuthUser, Depends(jwt_middleware)],
    limit: int = 100,
    page: int = 1,
    q: Optional[str] = None,
):
    # Cek apakah role pengguna adalah ADMIN atau HR
    users, total_rows, total_pages = user_service.list()

    return {
        "data": [
            {
                "id": user.id,
                "full_name": user.full_name,
                "username": user.username,
                "roles": [role.name for role in user.roles],
                "created_at": user.created_at,
                "updated_at": user.updated_at,
            }
            for user in users
        ],
        "meta": {
            "limit": limit,
            "page": page,
            "total_rows": total_rows,
            "total_pages": total_pages,
        },
    }


@router.post("/user")
def user_create(
    auth_user: Annotated[AuthUser, Depends(jwt_middleware)],
        body: UserCreate
):
    # Check if the user has the 'ADMIN' role
    if not auth_user.roles or ROLE_ADMIN not in auth_user.roles:
        raise HTTPException(
            status_code=403,
            detail="Access denied: Only ADMIN role can create a new user."
        )

    user = user_service.create(body)

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

@router.put("/user/{id}")
def user_update(
    auth_user: Annotated[AuthUser, Depends(jwt_middleware)],
        id: int,
        body: UserUpdate
):
    # Check if the user has the 'ADMIN' role
    if not auth_user.roles or ROLE_ADMIN not in auth_user.roles:
        raise HTTPException(
            status_code=403,
            detail="Access denied: Only ADMIN role can update user."
        )

    user = user_service.update(id, body)

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

@router.delete("/user/{id}")
def user_delete(
    auth_user: Annotated[AuthUser, Depends(jwt_middleware)],
    id: int
):
    # Check if the user has the 'ADMIN' role
    if not auth_user.roles or ROLE_ADMIN not in auth_user.roles:
        raise HTTPException(
            status_code=403,
            detail="Access denied: Only ADMIN role can delete user"
        )

    user_service.delete(id)
    return {"message": "User deleted successfully"}

# @router.put("/user/update_user_password")
# def user_update(
#     auth_user: Annotated[AuthUser, Depends(jwt_middleware)], body: PasswordUpdate
# ):
#     auth_service.user_exists(auth_user.id)
#     user = user_service.update_user_password(auth_user.id,body)
#     return {"message": "Password updated successfully"}

@router.put("/change_password/{id}")
def user_update(
    auth_user: Annotated[AuthUser, Depends(jwt_middleware)],
    id: int, body: RegisterUpdate
):
    # Check if the user has the 'ADMIN' role
    if not auth_user.roles or ROLE_ADMIN not in auth_user.roles:
        raise HTTPException(
            status_code=403,
            detail="Access denied: Only ADMIN role can change password"
        )

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