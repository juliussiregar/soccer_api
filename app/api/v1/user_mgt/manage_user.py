from fastapi import APIRouter, Depends
from typing import Optional, Annotated

from app.schemas.user_mgt import UserFilter, UserCreate, UserUpdate,PasswordUpdate
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
    auth_service.has_role(auth_user.id, ROLE_ADMIN)

    filter = UserFilter(limit=limit, page=page, search=q)
    users, total_rows, total_pages = user_service.list(filter)

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
    auth_user: Annotated[AuthUser, Depends(jwt_middleware)], body: UserCreate
):
    auth_service.has_role(auth_user.id, ROLE_ADMIN)

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

@router.put("/user/update_user_password")
def user_update(
    auth_user: Annotated[AuthUser, Depends(jwt_middleware)], body: PasswordUpdate
):
    auth_service.user_exists(auth_user.id)
    user = user_service.update_user_password(auth_user.id,body)
    return {"message": "Password updated successfully"}

# @router.put("/user/{id}")
# def user_update(
#     auth_user: Annotated[AuthUser, Depends(jwt_middleware)], id: int, body: UserUpdate
# ):
#     auth_service.has_role(auth_user.id, ROLE_ADMIN)

#     user = user_service.update(id, body)

#     return {
#         "data": {
#             "id": user.id,
#             "full_name": user.full_name,
#             "username": user.username,
#             "referral_code": user.referral_code,
#             "profit_share": user.profit_share,
#             "created_at": user.created_at,
#             "updated_at": user.updated_at,
#         },
#     }
