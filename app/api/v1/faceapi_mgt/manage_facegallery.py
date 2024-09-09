from fastapi import  HTTPException,APIRouter, Depends, File, UploadFile
from typing import Optional, Annotated
from app.core.constants.auth import ROLE_ADMIN
from app.schemas.faceapi_mgt import CreateFaceGallery
from app.clients.face_api import FaceApiClient
from app.services.auth import AuthService
# from app.services.face_api import FaceApiService
from app.middleware.jwt import jwt_middleware, AuthUser

client = FaceApiClient()
router = APIRouter()
# service = FaceApiService()
auth_service = AuthService()





@router.post("/create-facegallery")
def create_facegallery(auth_user: Annotated[AuthUser, Depends(jwt_middleware)],request_body: CreateFaceGallery):
    auth_service.has_role(auth_user.id, ROLE_ADMIN)
    try:
        # Menggunakan klien API untuk mengirim data
        result = client.create_facegallery(request_body)
        # result = service.insert_facegallery(request_body)
        return result
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)

@router.get("/my-facegalleries")
def get_facegalleries(auth_user: Annotated[AuthUser, Depends(jwt_middleware)]):
    auth_service.has_role(auth_user.id, ROLE_ADMIN)
    try:
        # Menggunakan klien API untuk mengirim data
        result = client.get_facegallery()
        # result = service.insert_facegallery(request_body)
        return result
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    