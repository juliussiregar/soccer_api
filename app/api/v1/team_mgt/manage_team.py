from fastapi import APIRouter, Depends, HTTPException
from typing import Optional, Annotated
from app.schemas.team import TeamCreate, TeamUpdate
from app.middleware.jwt import jwt_middleware, AuthUser
from app.core.constants.auth import ROLE_ADMIN
from app.services.team import TeamService

router = APIRouter()
team_service = TeamService()


@router.post("/team", description="Create a new team")
def create_team(
    auth_user: Annotated[AuthUser, Depends(jwt_middleware)],
    body: TeamCreate,
):
    # Check if the user has the 'ADMIN' role
    if not auth_user.roles or ROLE_ADMIN not in auth_user.roles:
        raise HTTPException(
            status_code=403,
            detail="Access denied: Only ADMIN role can create a new team."
        )

    try:
        team = team_service.create(body.dict())
        return {
            "data": {
                "id": team.id,
                "team_name": team.team_name,
                "team_logo": team.team_logo,
                "coach_name": team.coach_name,
                "total_players": team.total_players,
                "created_at": team.created_at,
                "updated_at": team.updated_at,
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/team/{id}", description="Get a team by ID")
def get_team(
    auth_user: Annotated[AuthUser, Depends(jwt_middleware)],
    id: int,
):
    # Check if the user has the 'ADMIN' role
    if not auth_user.roles or ROLE_ADMIN not in auth_user.roles:
        raise HTTPException(
            status_code=403,
            detail="Access denied: Only ADMIN role can view team details."
        )

    try:
        team = team_service.find_by_id(id)
        return {
            "data": {
                "id": team.id,
                "team_name": team.team_name,
                "team_logo": team.team_logo,
                "coach_name": team.coach_name,
                "total_players": team.total_players,
                "created_at": team.created_at,
                "updated_at": team.updated_at,
            }
        }
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put("/team/{id}", description="Update a team")
def update_team(
    auth_user: Annotated[AuthUser, Depends(jwt_middleware)],
    id: int,
    body: TeamUpdate,
):
    # Check if the user has the 'ADMIN' role
    if not auth_user.roles or ROLE_ADMIN not in auth_user.roles:
        raise HTTPException(
            status_code=403,
            detail="Access denied: Only ADMIN role can update team details."
        )

    try:
        team = team_service.update(id, body.dict())
        return {
            "data": {
                "id": team.id,
                "team_name": team.team_name,
                "team_logo": team.team_logo,
                "coach_name": team.coach_name,
                "total_players": team.total_players,
                "created_at": team.created_at,
                "updated_at": team.updated_at,
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/team/{id}", description="Delete a team")
def delete_team(
    auth_user: Annotated[AuthUser, Depends(jwt_middleware)],
    id: int,
):
    # Check if the user has the 'ADMIN' role
    if not auth_user.roles or ROLE_ADMIN not in auth_user.roles:
        raise HTTPException(
            status_code=403,
            detail="Access denied: Only ADMIN role can delete a team."
        )

    try:
        team_service.delete(id)
        return {"message": "Team deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/team", description="List all teams with pagination and search")
def list_teams(
    auth_user: Annotated[AuthUser, Depends(jwt_middleware)],
    limit: int = 20,
    page: int = 1,
    q: Optional[str] = None,
):
    # Check if the user has the 'ADMIN' role
    if not auth_user.roles or ROLE_ADMIN not in auth_user.roles:
        raise HTTPException(
            status_code=403,
            detail="Access denied: Only ADMIN role can list teams."
        )

    try:
        teams, total_rows, total_pages = team_service.list(limit, page, q)
        return {
            "data": [
                {
                    "id": team.id,
                    "team_name": team.team_name,
                    "team_logo": team.team_logo,
                    "coach_name": team.coach_name,
                    "total_players": team.total_players,
                    "created_at": team.created_at,
                    "updated_at": team.updated_at,
                }
                for team in teams
            ],
            "meta": {
                "limit": limit,
                "page": page,
                "total_rows": total_rows,
                "total_pages": total_pages,
            },
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
