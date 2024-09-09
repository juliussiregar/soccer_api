from fastapi import APIRouter

from app.api.v1.user_mgt import manage_user, manage_register

router = APIRouter(tags=["User Management"])

router.include_router(manage_user.router)
router.include_router(manage_register.router)
