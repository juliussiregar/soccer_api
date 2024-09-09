from fastapi import APIRouter

from app.api.v1.faceapi_mgt import manage_facegallery,manage_face


router = APIRouter(tags=["Face Management"])

router.include_router(manage_facegallery.router)
router.include_router(manage_face.router)
