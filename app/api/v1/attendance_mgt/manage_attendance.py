import base64
from datetime import date, datetime
from fastapi import  HTTPException,APIRouter, Depends, File, Query, UploadFile
from typing import Optional, Annotated
from app.core.constants.auth import ROLE_ADMIN
from app.schemas.attendance_mgt import AttendanceFilter
from app.schemas.visitor import IdentifyVisitorFace,IdentifyVisitor, VisitorFilter
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


@router.get('/visitor-monitoring/visitors-today')
def get_attendances_today(
    # auth_user: Annotated[AuthUser, Depends(jwt_middleware)],
    date: date = datetime.now().date(),
    ):
    # auth_service.has_role(auth_user.id, ROLE_ADMIN)
    
    visitors = attendance_service.list(date)
    return {
        "visitors": [
            {
                "id": visitor.id,
                "full_name": visitor.visitor.full_name,
                "company_name": visitor.visitor.company,
                "clock_in_time": visitor.Check_in.strftime("%d-%m-%Y %H:%M"),
                "clock_out_time": visitor.Check_out.strftime("%d-%m-%Y %H:%M") if visitor.Check_out else None,
                "total_time": str(visitor.Check_out - visitor.Check_in)[:-7] if visitor.Check_out else None,

            }
            for visitor in visitors
        ]
    }

@router.get('/visitor-monitoring/visitors-by-date')
def get_attendances_by_day(
    # auth_user: Annotated[AuthUser, Depends(jwt_middleware)],
    date: date ,
    ):
    # auth_service.has_role(auth_user.id, ROLE_ADMIN)
    
    visitors = attendance_service.list(date)
    return {
        "visitors": [
            {
                "id": visitor.id,
                "full_name": visitor.visitor.full_name,
                "company_name": visitor.visitor.company,
                "clock_in_time": visitor.Check_in.strftime("%d-%m-%Y %H:%M"),
                "clock_out_time": visitor.Check_out.strftime("%d-%m-%Y %H:%M") if visitor.Check_out else None,
                "total_time": str(visitor.Check_out - visitor.Check_in)[:-7] if visitor.Check_out else None,
            }
            for visitor in visitors
        ]
    }


@router.post('/attendance/check-in')
def attendance_check_in( 
    # auth_user: Annotated[AuthUser, Depends(jwt_middleware)],
    # client_name:Optional[str]=None,file: UploadFile = File(...)
    request_body :IdentifyVisitor):
    # auth_service.has_role(auth_user.id,ROLE_ADMIN)
    attendances,visitors= attendance_service.create(request_body)

    return {
        'status':200,
        'message':'Visitor is Valid',
        'visitor':
            {
                'fullName':visitors.full_name,
                'nik':visitors.nik,
                'address':visitors.address,
                'companyName':visitors.company,
                'attendance':{
                    'check_in': attendances.Check_in,
                    'check_out':attendances.Check_out,
                    'created_at':attendances.created_at
                },
                'message':"Check-In Successful!, WELCOME!!"

            }        
    } 

@router.put('/attendance/check-out')
def attendance_check_out(
    # auth_user: Annotated[AuthUser, Depends(jwt_middleware)],
    # client_name:Optional[str]=None,file: UploadFile = File(...)
    request_body :IdentifyVisitor
    ):
    # auth_service.has_role(auth_user.id,ROLE_ADMIN)
    attendances, visitors = attendance_service.update(request_body)

    return {
        'status':200,
        'message':'Visitor is Valid',
        'visitor':
            {
                'fullName':visitors.full_name,
                'nik':visitors.nik,
                'address':visitors.address,
                'companyName':visitors.company,
                'attendance':{
                    'check_in': attendances.Check_in,
                    'check_out':attendances.Check_out,
                    'created_at':attendances.created_at
                },
                'message':"Check-Out Successful! , SEE YOUUU"

            }        
    } 
