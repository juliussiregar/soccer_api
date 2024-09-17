import base64
from fastapi import  HTTPException,APIRouter, Depends, File, UploadFile
from typing import Optional, Annotated
from app.core.constants.auth import ROLE_ADMIN
from app.schemas.visitor import IdentifyVisitorFace
from app.schemas.faceapi_mgt import IdentifyFace

from app.clients.face_api import FaceApiClient
from app.services.auth import AuthService
from app.services.visitor import VisitorService
from app.services.attendance import AttendanceService
from app.middleware.jwt import jwt_middleware, AuthUser

client = FaceApiClient()
router = APIRouter()
auth_service = AuthService()
visitor_service = VisitorService()
attendance_service = AttendanceService()


@router.post('/attendance/check-in')
def attendance_check_in( auth_user: Annotated[AuthUser, Depends(jwt_middleware)],client_name:Optional[str]=None,file: UploadFile = File(...)):
    auth_service.has_role(auth_user.id,ROLE_ADMIN)
    attendances,visitors= attendance_service.create(client_name,file)

    return {
        'status':200,
        'message':'Visitor is Valid',
        'data':
            {
                'user_name':visitors.username,
                'nik':visitors.nik,
                'email':visitors.email,
                'company':visitors.company,
                'attendance':{
                    'check_in': attendances.Check_in,
                    'check_out':attendances.Check_out,
                    'created_at':attendances.created_at
                }

            }        
    } 

@router.put('/attendance/check-out')
def attendance_check_out(auth_user: Annotated[AuthUser, Depends(jwt_middleware)],client_name:Optional[str]=None,file: UploadFile = File(...)):
    auth_service.has_role(auth_user.id,ROLE_ADMIN)
    attendances, visitors = attendance_service.update(client_name,file)

    return {
        'status':200,
        'message':'Visitor is Valid',
        'data':
            {
                'user_name':visitors.username,
                'nik':visitors.nik,
                'email':visitors.email,
                'company':visitors.company,
                'attendance':{
                    'check_in': attendances.Check_in,
                    'check_out':attendances.Check_out,
                    'updated_at':attendances.updated_at
                }

            }        
    } 
