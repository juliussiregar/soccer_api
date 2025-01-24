# v1/__init__.py

from fastapi import APIRouter
from app.api.v1.auth import router as auth_router
from app.api.v1.user_mgt import router as user_router
from app.api.v1.team_mgt import router as team_router
from app.api.v1.guardian_mgt import router as guardian_router
from app.api.v1.official_mgt import router as official_router
from app.api.v1.player_mgt import router as player_router
from app.api.v1.team_application_mgt import router as team_application_router


router = APIRouter(prefix="/v1")
router.include_router(auth_router)
router.include_router(user_router)
router.include_router(team_router)
router.include_router(guardian_router)
router.include_router(official_router)
router.include_router(player_router)
router.include_router(team_application_router)

