from fastapi import APIRouter, Depends, HTTPException
from typing import Optional, Annotated

from app.schemas.user_mgt import RegisterGuardian, UserCreate, UserUpdate, RegisterUpdate, UserFilter, RegisterOfficial

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
    limit: int = 20,  # Default limit jika tidak diberikan
    page: int = 1,  # Default page jika tidak diberikan
    q: Optional[str] = None,  # Query untuk pencarian full_name
):
    
    # Check if the user has the 'ADMIN' role
    if not auth_user.roles or ROLE_ADMIN not in auth_user.roles:
        raise HTTPException(
            status_code=403,
            detail="Access denied: Only ADMIN role can get all user"
        )
    # Buat filter berdasarkan parameter
    filter = UserFilter(limit=limit, page=page, search=q)

    # Ambil data user menggunakan filter
    users, total_rows, total_pages = user_service.list(filter)

    return {
        "data": [
            {
                "id": user.id,
                "full_name": user.full_name,
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
    # auth_user: Annotated[AuthUser, Depends(jwt_middleware)],
        body: UserCreate
):
    # # Check if the user has the 'ADMIN' role
    # if not auth_user.roles or ROLE_ADMIN not in auth_user.roles:
    #     raise HTTPException(
    #         status_code=403,
    #         detail="Access denied: Only ADMIN role can create a new user."
    #     )

    user = user_service.create(body)

    return {
        "data": {
            "id": user.id,
            "full_name": user.full_name,
            "email": user.email,
            "roles": [body.role],
            "created_at": user.created_at,
            "updated_at": user.updated_at,
        },
    }
    
@router.post("/register/guardian", description="Register Guardian")
def register_guardian(
    body: RegisterGuardian
):
    user = user_service.create_guardian(body)
    guardian = user.guardian_profile  # Ambil data guardian dari relasi user

    return {
        "data": {
            "id": user.id,
            "full_name": user.full_name,
            "email": user.email,
            "roles": ["GUARDIAN"],  # Role otomatis GUARDIAN
            "created_at": user.created_at,
            "guardian": {
                "id": guardian.id,
                "birth_date": guardian.birth_date,
                "kartu_keluarga": guardian.kartu_keluarga,
                "ktp": guardian.ktp,
                "phone_number": guardian.phone_number,
                "address": guardian.address
            }
        },
    }
    
@router.post("/register/official", description="Register Official")
def register_official(
    body: RegisterOfficial
):
    user = user_service.create_official(body)
    official = user.official_profile  # Ambil data official dari relasi user

    return {
        "data": {
            "id": user.id,
            "full_name": user.full_name,
            "email": user.email,
            "roles": ["OFFICIAL"],  # Role otomatis OFFICIAL
            "created_at": user.created_at,
            "official": {
                "id": official.id,
                "name": official.name,
                "position": official.position.value,
                "profile_picture": official.profile_picture,
                "created_at": official.created_at,
                "updated_at": official.updated_at,
            }
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
            "email": user.email,
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
            "email": user.email,
            "created_at": user.created_at,
            "updated_at": user.updated_at,
        },
    }