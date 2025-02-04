from fastapi import APIRouter, Depends, HTTPException
from typing import Annotated, List
from app.schemas.official import OfficialCreate, OfficialUpdate, OfficialResponse
from app.middleware.jwt import jwt_middleware, AuthUser
from app.services.official import OfficialService
from app.core.constants.auth import ROLE_ADMIN, ROLE_OFFICIAL

router = APIRouter()
official_service = OfficialService()

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
    
    
@router.get("/officials/my-team", response_model=dict, description="Get all officials in the same team as the logged-in official")
def get_officials_in_same_team(auth_user: Annotated[AuthUser, Depends(jwt_middleware)]):
    # Cek apakah user memiliki role OFFICIAL
    if not auth_user.roles or ROLE_OFFICIAL not in auth_user.roles:
        raise HTTPException(status_code=403, detail="Access denied: Only OFFICIAL role can access this resource.")

    # Ambil team_id dari token login
    team_id = auth_user.team_id
    if not team_id:
        raise HTTPException(status_code=400, detail="User is not associated with any team.")

    try:
        officials = official_service.get_officials_in_same_team(team_id)
        return {
            "data": [OfficialResponse(id=official.id, name=official.name, position=official.position, profile_picture=official.profile_picture) for official in officials]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
