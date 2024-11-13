# v1/position_mgt/__init__.py

from fastapi import APIRouter
from app.api.v1.position_mgt.manage_position import router as position_router

router = APIRouter(tags=["Position Management"])
router.include_router(position_router)
