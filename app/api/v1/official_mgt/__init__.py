from fastapi import APIRouter

from app.api.v1.official_mgt import manage_official

router = APIRouter(tags=["Official Management"])

router.include_router(manage_official.router)
