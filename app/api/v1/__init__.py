from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.user_mgt import router as user_router
from app.api.v1.faceapi_mgt import router as faceapi_router
from app.api.v1.vistor_mgt import router as visitor_router
from app.api.v1.attendance_mgt import router as attendace_router


router = APIRouter(prefix="/v1")
router.include_router(auth_router)
router.include_router(user_router)
router.include_router(faceapi_router)
router.include_router(visitor_router)
router.include_router(attendace_router)