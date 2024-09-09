from fastapi import APIRouter

from app.api.v1.auth import manage_auth

router = APIRouter(tags=["Authentication"])

router.include_router(manage_auth.router)
