from fastapi import APIRouter
from app.api.v1.face_mgt.manage_face import router as manage_face_router

router = APIRouter(tags=["Face Management"])
router.include_router(manage_face_router)
