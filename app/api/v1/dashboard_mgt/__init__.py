from fastapi import APIRouter

from app.api.v1.dashboard_mgt import manage_dashboard


router = APIRouter(tags=["Dashboard Management"])

router.include_router(manage_dashboard.router)
