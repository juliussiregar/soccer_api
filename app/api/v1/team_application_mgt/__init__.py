from fastapi import APIRouter

from app.api.v1.team_application_mgt import manage_team_application

router = APIRouter(tags=["Team Application Management"])

router.include_router(manage_team_application.router)
