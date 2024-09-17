import base64
from fastapi import File, HTTPException, APIRouter, Depends, UploadFile
from typing import Annotated, Optional
from app.core.constants.auth import ROLE_ADMIN
from app.schemas.faceapi_mgt import CreateEnrollFace,GetEnrollFace,IdentifyFace
from app.clients.face_api import FaceApiClient
from app.services.auth import AuthService
from app.middleware.jwt import jwt_middleware, AuthUser

client = FaceApiClient()
router = APIRouter()
auth_service = AuthService()

@router.post("/enroll-face")
async def create_enroll_face(auth_user: Annotated[AuthUser, Depends(jwt_middleware)],request_body: CreateEnrollFace = Depends(),file: UploadFile = File(...)):
    auth_service.has_role(auth_user.id, ROLE_ADMIN)
    try:
        file_content = await file.read()
        
        value = client.create_faces(request_body,file_content)

        return value
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    
@router.get("/list-faces")
def get_enroll_face(auth_user: Annotated[AuthUser, Depends(jwt_middleware)],facegallery_id:str,trx_id:str):
    auth_service.has_role(auth_user.id, ROLE_ADMIN)
    try:
        # Menggunakan klien API untuk mengirim data
        result = client.get_listface(facegallery_id,trx_id)
        return result
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)


@router.post("/identify-face")
async def create_enroll_face(auth_user: Annotated[AuthUser, Depends(jwt_middleware)],request_body: IdentifyFace = Depends(),file: UploadFile = File(...)):
    auth_service.has_role(auth_user.id, ROLE_ADMIN)
    try:
        file_content = await file.read()
        value = client.identify_face(request_body,file_content)

        return value
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)