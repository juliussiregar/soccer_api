from fastapi import APIRouter

from app.api.test import test

router = APIRouter(tags=["TEST API"])

router.include_router(test.router)
