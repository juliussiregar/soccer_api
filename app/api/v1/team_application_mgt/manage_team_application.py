import logging
from fastapi import APIRouter, Depends, HTTPException, logger
from typing import Annotated
from app.models.guardian import Guardian
from app.models.team_official import TeamOfficial
from app.schemas.team_application import TeamApplicationCreate, TeamApplicationUpdate
from app.middleware.jwt import jwt_middleware, AuthUser
from app.services.team_application import TeamApplicationService
from app.core.constants.auth import ROLE_GUARDIAN, ROLE_OFFICIAL, ROLE_PLAYER
 # Kumpulkan semua player_id yang terikat dengan guardian_id
from app.models.guardian_player import GuardianPlayer
from app.models.team_application import TeamApplication
from app.models.team import Team
from app.core.database import get_session

router = APIRouter()
team_application_service = TeamApplicationService()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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
    if not auth_user.roles or ROLE_OFFICIAL not in auth_user.roles:
        raise HTTPException(
            status_code=403,
            detail="Access denied: Only OFFICIAL role can update application status."
        )

    with get_session() as db:  # Pastikan sesi tetap terbuka
        application = db.query(TeamApplication).filter(TeamApplication.id == application_id).first()

        if not application:
            raise HTTPException(status_code=404, detail="Application not found")

        # Load team & team_officials secara eksplisit sebelum sesi tertutup
        application.team.team_officials
 

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



@router.get("/team/application/player", description="Get applications by player ID (GUARDIAN)")
def get_applications_by_player(
    auth_user: Annotated[AuthUser, Depends(jwt_middleware)],
):
    if not auth_user.roles or ROLE_GUARDIAN not in auth_user.roles:
        logger.warning(f"Unauthorized access attempt by user_id {auth_user.id}")
        raise HTTPException(
            status_code=403,
            detail="Access denied: Only GUARDIAN role can view applications.",
        )

    try:
        # Cari guardian_id berdasarkan user_id
        with get_session() as db:
            guardian = db.query(Guardian).filter(Guardian.user_id == auth_user.id).first()
            if not guardian:
                logger.warning(f"No guardian found for user_id {auth_user.id}")
                raise HTTPException(status_code=404, detail="Guardian profile not found.")

            guardian_id = guardian.id
            logger.info(f"Authenticated guardian_id: {guardian_id}")

            # Ambil semua player_id yang terkait dengan guardian_id
            guardian_players = (
                db.query(GuardianPlayer.player_id)
                .filter(GuardianPlayer.guardian_id == guardian_id)
                .all()
            )
            player_ids = [gp.player_id for gp in guardian_players]

        logger.info(f"Player IDs linked to guardian_id {guardian_id}: {player_ids}")

        # Cari aplikasi berdasarkan player_ids
        applications = team_application_service.find_by_player_ids(player_ids)
        logger.info(f"Applications found for player_ids {player_ids}: {applications}")

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
        logger.error(f"Error fetching applications: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch applications.")


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

@router.get("/team/applications", description="Get all applications for the team (OFFICIAL only)")
def get_applications_by_team(
    auth_user: Annotated[AuthUser, Depends(jwt_middleware)]
):
    # Hanya OFFICIAL yang bisa mengakses endpoint ini
    if not auth_user.roles or ROLE_OFFICIAL not in auth_user.roles:
        raise HTTPException(
            status_code=403,
            detail="Access denied: Only OFFICIAL role can view applications for their team."
        )

    try:
        # Dapatkan aplikasi berdasarkan user_id yang sedang login
        applications = team_application_service.get_applications_by_user_id(auth_user.id)

        # Format response dengan name (nama pemain)
        return {
            "data": [
                {
                    "id": app.id,
                    "player_id": app.player_id,
                    "name": app.name,  # Tambahkan nama pemain
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
