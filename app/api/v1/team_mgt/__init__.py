from fastapi import APIRouter

from app.api.v1.team_mgt import manage_team

router = APIRouter(tags=["Team Management"])

router.include_router(manage_team.router)
