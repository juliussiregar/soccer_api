from fastapi import  HTTPException,APIRouter, Depends, File, UploadFile
from typing import Optional, Annotated
from app.core.constants.auth import ROLE_ADMIN
from app.schemas.faceapi_mgt import CreateFaceGallery
from app.clients.face_api import FaceApiClient
from app.services.auth import AuthService
from app.services.client import ClientService
from app.middleware.jwt import jwt_middleware, AuthUser

clients = FaceApiClient()
router = APIRouter()
client_service = ClientService()
auth_service = AuthService()





@router.post("/create-facegallery")
def create_facegallery(auth_user: Annotated[AuthUser, Depends(jwt_middleware)],client_name:str):
    auth_service.has_role(auth_user.id, ROLE_ADMIN)
    try:
        # Menggunakan klien API untuk mengirim data
        # result = clients.create_facegallery(request_body)
        result = client_service.insert_facegallery(client_name)
        return result
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)

@router.get("/my-facegalleries")
def get_facegalleries(auth_user: Annotated[AuthUser, Depends(jwt_middleware)]):
    auth_service.has_role(auth_user.id, ROLE_ADMIN)
    try:
        # Menggunakan klien API untuk mengirim data
        result = clients.get_facegallery()
        # result = service.insert_facegallery(request_body)
        return result
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    