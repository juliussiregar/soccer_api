from fastapi import APIRouter, Depends, HTTPException
from typing import Annotated
from app.schemas.official import OfficialCreate, OfficialUpdate
from app.middleware.jwt import jwt_middleware, AuthUser
from app.services.official import OfficialService
from app.core.constants.auth import ROLE_ADMIN, ROLE_OFFICIAL

router = APIRouter()
official_service = OfficialService()


@router.post("/official/register", description="Register an official profile")
def register_official(
    auth_user: Annotated[AuthUser, Depends(jwt_middleware)],
    body: OfficialCreate,
):
    # Check if the user has the 'OFFICIAL' role
    if not auth_user.roles or ROLE_OFFICIAL not in auth_user.roles:
        raise HTTPException(
            status_code=403,
            detail="Access denied: Only OFFICIAL role can register an official profile."
        )

    try:
        payload = body.dict()
        payload["user_id"] = auth_user.id  # Associate the logged-in user
        official = official_service.create(payload)
        return {
            "data": {
                "id": official.id,
                "name": official.name,
                "position": official.position,
                "profile_picture": official.profile_picture,
                "created_at": official.created_at,
                "updated_at": official.updated_at,
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/official-me", description="Get the logged-in official profile")
def get_official(auth_user: Annotated[AuthUser, Depends(jwt_middleware)]):
    # Check if the user has the 'OFFICIAL' role
    if not auth_user.roles or ROLE_OFFICIAL not in auth_user.roles:
        raise HTTPException(
            status_code=403,
            detail="Access denied: Only OFFICIAL role can view the official profile."
        )

    try:
        official = official_service.find_by_user_id(auth_user.id)
        if not official:
            raise HTTPException(status_code=404, detail="Official profile not found.")

        return {
            "data": {
                "id": official.id,
                "name": official.name,
                "position": official.position,
                "profile_picture": official.profile_picture,
                "created_at": official.created_at,
                "updated_at": official.updated_at,
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/official", description="Update the logged-in official profile")
def update_official(
    auth_user: Annotated[AuthUser, Depends(jwt_middleware)],
    body: OfficialUpdate,
):
    # Check if the user has the 'OFFICIAL' role
    if not auth_user.roles or ROLE_OFFICIAL not in auth_user.roles:
        raise HTTPException(
            status_code=403,
            detail="Access denied: Only OFFICIAL role can update the official profile."
        )

    try:
        payload = body.dict(exclude_unset=True)  # Only include fields provided in the request
        official = official_service.update(auth_user.id, payload)
        return {
            "data": {
                "id": official.id,
                "name": official.name,
                "position": official.position,
                "profile_picture": official.profile_picture,
                "created_at": official.created_at,
                "updated_at": official.updated_at,
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/officials", description="List all officials (ADMIN only)")
def list_all_officials(
    auth_user: Annotated[AuthUser, Depends(jwt_middleware)],
    limit: int = 20,
    page: int = 1,
):
    # Check if the user has the 'ADMIN' role
    if not auth_user.roles or ROLE_ADMIN not in auth_user.roles:
        raise HTTPException(
            status_code=403,
            detail="Access denied: Only ADMIN role can view all officials."
        )

    try:
        officials, total = official_service.list(limit=limit, page=page)
        total_pages = (total + limit - 1) // limit  # Calculate total pages

        return {
            "data": [
                {
                    "id": official.id,
                    "name": official.name,
                    "position": official.position,
                    "profile_picture": official.profile_picture,
                    "created_at": official.created_at,
                    "updated_at": official.updated_at,
                }
                for official in officials
            ],
            "meta": {
                "limit": limit,
                "page": page,
                "total_rows": total,
                "total_pages": total_pages,
            },
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
