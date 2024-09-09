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
auth_service = AuthService()


# @router.app('/register/visitor'):
# def register_visitor(auth_user: Annotated[AuthUser, Depends(jwt_middleware)]):

    