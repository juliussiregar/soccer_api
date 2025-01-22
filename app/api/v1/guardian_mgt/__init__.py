from fastapi import APIRouter

from app.api.v1.guardian_mgt import manage_guardian

router = APIRouter(tags=["guardian Management"])

router.include_router(manage_guardian.router)
