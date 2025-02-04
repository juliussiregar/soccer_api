import logging
from fastapi import APIRouter, Depends, HTTPException, logger
from typing import Annotated
from app.models.guardian import Guardian
from app.models.team_official import TeamOfficial
from app.schemas.team_application import TeamApplicationCreate, TeamApplicationUpdate, ApplicationTypes
from app.middleware.jwt import jwt_middleware, AuthUser
from app.services.team_application import TeamApplicationService
from app.core.constants.auth import ROLE_GUARDIAN, ROLE_OFFICIAL, ROLE_PLAYER
 # Kumpulkan semua player_id yang terikat dengan guardian_id
from app.models.guardian_player import GuardianPlayer
from app.models.team_application import TeamApplication
from app.models.team import Team
from app.models.player import Player
from app.core.database import get_session

router = APIRouter()
team_application_service = TeamApplicationService()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@router.post("/team/application", description="Create a team application (GUARDIAN only)")
def create_team_application(
    auth_user: Annotated[AuthUser, Depends(jwt_middleware)],
    body: TeamApplicationCreate
):
    # Hanya GUARDIAN yang bisa membuat aplikasi
    if not auth_user.roles or ROLE_GUARDIAN not in auth_user.roles:
        raise HTTPException(
            status_code=403,
            detail="Access denied: Only GUARDIAN role can create a team application."
        )

    try:
        payload = body.dict()
        payload["types"] = ApplicationTypes.APPLICATION.value  

        application = team_application_service.create(payload)
        return {
            "data": {
                "id": application.id,
                "player_id": application.player_id,
                "team_id": application.team_id,
                "status": application.status,
                "message": application.message,
                "types": application.types.value,  
                "created_at": application.created_at,
                "updated_at": application.updated_at,
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/team/invitation", description="Send a team invitation (OFFICIAL only)")
def create_team_invitation(
    auth_user: Annotated[AuthUser, Depends(jwt_middleware)],
    body: TeamApplicationCreate
):
    # Hanya OFFICIAL yang bisa mengirim undangan
    if not auth_user.roles or ROLE_OFFICIAL not in auth_user.roles:
        raise HTTPException(
            status_code=403,
            detail="Access denied: Only OFFICIAL role can send a team invitation."
        )

    try:
        payload = body.dict()
        payload["types"] = ApplicationTypes.INVITATION.value

        application = team_application_service.create(payload)
        return {
            "data": {
                "id": application.id,
                "player_id": application.player_id,
                "team_id": application.team_id,
                "status": application.status,
                "message": application.message,
                "types": application.types.value,  # Pastikan mengembalikan string
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



@router.get("/team/application/guardian", description="Get applications by Guardian ID (GUARDIAN)")
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
        with get_session() as db:
            # Cari guardian berdasarkan user_id
            guardian = db.query(Guardian).filter(Guardian.user_id == auth_user.id).first()
            if not guardian:
                logger.warning(f"No guardian found for user_id {auth_user.id}")
                raise HTTPException(status_code=404, detail="Guardian profile not found.")

            guardian_id = guardian.id

            # Ambil semua player_id yang terkait dengan guardian_id
            guardian_players = (
                db.query(GuardianPlayer.player_id)
                .filter(GuardianPlayer.guardian_id == guardian_id)
                .all()
            )
            player_ids = [gp.player_id for gp in guardian_players]

        if not player_ids:
            return {"data": []}

        # Cari aplikasi berdasarkan player_ids dengan JOIN ke tabel Player dan Team
        applications = (
            db.query(
                TeamApplication.id,
                TeamApplication.player_id,
                Player.name.label("player_name"),  # Ambil nama pemain
                TeamApplication.team_id,
                Team.team_name.label("team_name"),  # Ambil nama tim
                TeamApplication.status,
                TeamApplication.message,
                TeamApplication.created_at,
                TeamApplication.updated_at,
            )
            .join(Player, Player.id == TeamApplication.player_id)  # Join ke tabel Player
            .join(Team, Team.id == TeamApplication.team_id)  # Join ke tabel Team
            .filter(TeamApplication.player_id.in_(player_ids))
            .all()
        )

        # Return data dengan nama tim dan nama pemain
        return {
            "data": [
                {
                    "id": app.id,
                    "player_id": app.player_id,
                    "player_name": app.player_name,
                    "team_id": app.team_id,
                    "team_name": app.team_name,
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
def get_applications_by_team(auth_user: Annotated[AuthUser, Depends(jwt_middleware)]):
    try:
        logger.info(f"Fetching applications for user ID: {auth_user.id}, roles: {auth_user.roles}")

        # Validasi role
        if not auth_user.roles or ROLE_OFFICIAL not in auth_user.roles:
            raise HTTPException(
                status_code=403,
                detail="Access denied: Only OFFICIAL role can view applications for their team."
            )

        applications = team_application_service.get_applications_by_user_id(auth_user.id)
        logger.info(f"Found applications: {applications}")

        return {"data": applications}
    except Exception as e:
        logger.error(f"Error fetching team applications: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))