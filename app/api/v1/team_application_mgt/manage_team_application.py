from fastapi import APIRouter, Depends, HTTPException
from typing import Annotated
from app.schemas.team_application import TeamApplicationCreate, TeamApplicationUpdate
from app.middleware.jwt import jwt_middleware, AuthUser
from app.services.team_application import TeamApplicationService
from app.core.constants.auth import ROLE_GUARDIAN, ROLE_OFFICIAL, ROLE_PLAYER

router = APIRouter()
team_application_service = TeamApplicationService()


@router.post("/team/application", description="Create a team application (GUARDIAN only)")
def create_team_application(
    auth_user: Annotated[AuthUser, Depends(jwt_middleware)],
    body: TeamApplicationCreate,
):
    # Hanya GUARDIAN yang bisa membuat aplikasi
    if not auth_user.roles or ROLE_GUARDIAN not in auth_user.roles:
        raise HTTPException(
            status_code=403,
            detail="Access denied: Only GUARDIAN role can create a team application."
        )

    try:
        payload = body.dict()
        application = team_application_service.create(payload)
        return {
            "data": {
                "id": application.id,
                "player_id": application.player_id,
                "team_id": application.team_id,
                "status": application.status,
                "message": application.message,
                "created_at": application.created_at,
                "updated_at": application.updated_at,
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/team/application/{application_id}", description="Update application status (OFFICIAL only)")
def update_application_status(
    application_id: int,
    auth_user: Annotated[AuthUser, Depends(jwt_middleware)],
    body: TeamApplicationUpdate,
):
    # Hanya OFFICIAL yang terdaftar dalam team official yang bisa mengubah status
    if not auth_user.roles or ROLE_OFFICIAL not in auth_user.roles:
        raise HTTPException(
            status_code=403,
            detail="Access denied: Only OFFICIAL role can update application status."
        )

    try:
        application = team_application_service.find_by_id(application_id)

        # Pastikan official terdaftar di tim yang bersangkutan
        if auth_user.id not in [official.official_id for official in application.team.team_officials]:
            raise HTTPException(
                status_code=403,
                detail="Access denied: You are not associated with this team."
            )

        updated_application = team_application_service.update_status(application_id, body.status)
        return {
            "data": {
                "id": updated_application.id,
                "player_id": updated_application.player_id,
                "team_id": updated_application.team_id,
                "status": updated_application.status,
                "message": updated_application.message,
                "created_at": updated_application.created_at,
                "updated_at": updated_application.updated_at,
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/team/application/player", description="Get applications by player ID (GUARDIAN or PLAYER)")
def get_applications_by_player(
    auth_user: Annotated[AuthUser, Depends(jwt_middleware)],
):
    # Hanya GUARDIAN atau PLAYER yang bisa mendapatkan aplikasi berdasarkan player ID
    if not auth_user.roles or (ROLE_GUARDIAN not in auth_user.roles and ROLE_PLAYER not in auth_user.roles):
        raise HTTPException(
            status_code=403,
            detail="Access denied: Only GUARDIAN or PLAYER roles can view applications."
        )

    try:
        applications = team_application_service.find_by_player_id(auth_user.id)
        return {
            "data": [
                {
                    "id": app.id,
                    "player_id": app.player_id,
                    "team_id": app.team_id,
                    "status": app.status,
                    "message": app.message,
                    "created_at": app.created_at,
                    "updated_at": app.updated_at,
                }
                for app in applications
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/team/application/{application_id}", description="Delete a team application (GUARDIAN only)")
def delete_team_application(
    application_id: int,
    auth_user: Annotated[AuthUser, Depends(jwt_middleware)],
):
    # Hanya GUARDIAN yang bisa menghapus aplikasi
    if not auth_user.roles or ROLE_GUARDIAN not in auth_user.roles:
        raise HTTPException(
            status_code=403,
            detail="Access denied: Only GUARDIAN role can delete a team application."
        )

    try:
        team_application_service.delete(application_id)
        return {"message": "Team application deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
