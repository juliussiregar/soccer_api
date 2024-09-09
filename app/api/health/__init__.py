from fastapi import APIRouter

from app.api.health import healthcheck

router = APIRouter(tags=["Health Check"])

router.include_router(healthcheck.router)
