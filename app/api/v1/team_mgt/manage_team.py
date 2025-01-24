from fastapi import APIRouter, Depends, HTTPException
from typing import Annotated
from app.schemas.team import TeamCreate, TeamOfficialAssign, TeamUpdate
from app.middleware.jwt import jwt_middleware, AuthUser
from app.services.team import TeamService
from app.core.constants.auth import ROLE_ADMIN, ROLE_OFFICIAL

router = APIRouter()
team_service = TeamService()


@router.post("/team", description="Create a team")
def create_team(
    auth_user: Annotated[AuthUser, Depends(jwt_middleware)],
    body: TeamCreate,
):
    # Hanya ADMIN dan OFFICIAL yang dapat membuat tim
    if not auth_user.roles or (ROLE_ADMIN not in auth_user.roles and ROLE_OFFICIAL not in auth_user.roles):
        raise HTTPException(
            status_code=403,
            detail="Access denied: Only ADMIN or OFFICIAL roles can create a team."
        )

    try:
        # Jika pengguna adalah OFFICIAL, pastikan mereka hanya memiliki satu tim
        if ROLE_OFFICIAL in auth_user.roles:
            existing_team = team_service.find_by_official_id(auth_user.id)
            if existing_team:
                raise HTTPException(
                    status_code=403,
                    detail="Access denied: You can only create one team."
                )

        payload = body.dict()
        team = team_service.create(payload, auth_user.id)  # Masukkan official_id untuk TeamOfficial

        return {
            "data": {
                "id": team.id,
                "team_name": team.team_name,
                "team_logo": team.team_logo,
                "coach_name": team.coach_name,
                "total_players": 0,
                "created_at": team.created_at,
                "updated_at": team.updated_at,
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/team", description="Get the team associated with the logged-in official")
def get_team(
    auth_user: Annotated[AuthUser, Depends(jwt_middleware)],
):
    try:
        # Pastikan hanya OFFICIAL yang dapat mengakses endpoint ini
        if not auth_user.roles or ROLE_OFFICIAL not in auth_user.roles:
            raise HTTPException(
                status_code=403,
                detail="Access denied: Only OFFICIAL role can view the team."
            )

        # Cari tim berdasarkan user_id dari data login
        team = team_service.find_team_by_user_id(auth_user.id)
        if not team:
            raise HTTPException(
                status_code=404,
                detail="No team found for the logged-in official."
            )

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
    
@router.put("/team/update", description="Update a team associated with the logged-in official")
def update_team_by_user(
    auth_user: Annotated[AuthUser, Depends(jwt_middleware)],
    body: TeamUpdate,
):
    try:
        # Pastikan hanya OFFICIAL yang dapat mengakses endpoint ini
        if not auth_user.roles or ROLE_OFFICIAL not in auth_user.roles:
            raise HTTPException(
                status_code=403,
                detail="Access denied: Only OFFICIAL role can update the team."
            )

        payload = body.dict(exclude_unset=True)  # Hanya memperbarui field yang disediakan
        updated_team = team_service.update_team_by_user_id(auth_user.id, payload)

        return {
            "data": {
                "id": updated_team.id,
                "team_name": updated_team.team_name,
                "team_logo": updated_team.team_logo,
                "coach_name": updated_team.coach_name,
                "total_players": updated_team.total_players,
                "created_at": updated_team.created_at,
                "updated_at": updated_team.updated_at,
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/team/{team_id}", description="Delete a team by ID")
def delete_team(
    team_id: int,
    auth_user: Annotated[AuthUser, Depends(jwt_middleware)],
):
    try:
        team = team_service.find_by_id(team_id)

        # Hanya ADMIN atau pemilik tim (OFFICIAL) yang dapat menghapus tim ini
        if not auth_user.roles or (ROLE_ADMIN not in auth_user.roles and team.created_by != auth_user.id):
            raise HTTPException(
                status_code=403,
                detail="Access denied: You do not have permission to delete this team."
            )

        team_service.delete(team_id)
        return {"message": "Team deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.post("/team/assign-official", description="Assign an official to a team (ADMIN only)")
def assign_official(
    auth_user: Annotated[AuthUser, Depends(jwt_middleware)],
    body: TeamOfficialAssign,
):
    # Hanya ADMIN yang bisa meng-assign official ke tim
    if not auth_user.roles or ROLE_ADMIN not in auth_user.roles:
        raise HTTPException(
            status_code=403,
            detail="Access denied: Only ADMIN role can assign an official to a team."
        )

    try:
        assignment = team_service.assign_official(
            team_id=body.team_id,
            official_id=body.official_id
        )
        return {
            "message": "Official successfully assigned to the team.",
            "data": {
                "id": assignment.id,
                "team_id": assignment.team_id,
                "official_id": assignment.official_id,
                "created_at": assignment.created_at,
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/team/unassign-official", description="Unassign an official from a team (ADMIN only)")
def unassign_official(
    auth_user: Annotated[AuthUser, Depends(jwt_middleware)],
    body: TeamOfficialAssign,
):
    # Hanya ADMIN yang bisa menghapus assign official dari tim
    if not auth_user.roles or ROLE_ADMIN not in auth_user.roles:
        raise HTTPException(
            status_code=403,
            detail="Access denied: Only ADMIN role can unassign an official from a team."
        )

    try:
        team_service.unassign_official(
            team_id=body.team_id,
            official_id=body.official_id
        )
        return {"message": "Official successfully unassigned from the team."}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
