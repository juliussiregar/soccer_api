import base64
from fastapi import  HTTPException,APIRouter, Depends, File, UploadFile
from typing import Optional, Annotated
from app.core.constants.auth import ROLE_ADMIN
from app.schemas.visitor import CreateNewVisitor,GetVisitor,IdentifyVisitorFace
from app.schemas.faceapi_mgt import CreateEnrollFace,GetEnrollFace,IdentifyFace

from app.clients.face_api import FaceApiClient
from app.services.auth import AuthService
# from app.services.face_api import FaceApiService
from app.services.visitor import VisitorService
from app.middleware.jwt import jwt_middleware, AuthUser

client = FaceApiClient()
router = APIRouter()
auth_service = AuthService()
visitor_service = VisitorService()


@router.post('/register/visitor' ,description="Create new Visitor With Upload Picture")
# auth_user: Annotated[AuthUser, Depends(jwt_middleware)],
def register_visitor(request_body:CreateNewVisitor=Depends(),file: UploadFile = File(...)):

    visitors,clients,faces,transactions,face_api= visitor_service.create_visitor(request_body,file)

    return {
        "data": {
            "visitor": {
                "id": visitors.id,
                "username": visitors.username,
                "nik": visitors.nik,
                "born_date": visitors.born_date,
                "email": visitors.email,
                "company_name": visitors.company,
                "client_id":visitors.client_id,
                "created_at": visitors.created_at
            },
            "client": {
                "id": clients.id,
                "client_name": clients.client_name,
                "created_at": clients.created_at
            },
            "face": {
                "id": faces.id,
                "visitor_id": faces.visitor_id,
                "client_id": faces.client_id,
                "created_at": faces.created_at
            },
            "transaction": {
                "trx_id": transactions.id,
                "client_id": transactions.client_id,
                "visitor_id":transactions.visitor_id
            },
            "Riset-AI":face_api
            
        }
    }


@router.get('/get-visitor')
def get_visitorbyuser(username:str,nik:str):
    visitor,visitor_face = visitor_service.get_visitor(username,nik)

    return {
        "data": {
            "visitor": visitor,
            "visitor_face": visitor_face
        }
    }

@router.post('/identify-face-visitor')
def identify_face( client_name:Optional[str]=None,file: UploadFile = File(...)):
    result ,trancation= visitor_service.identify_face_visitor(client_name,file)   

    return {
        'status':200,
        'message':'Visitor is Valid',
        'data':
            {
                'user_name':result.username,
                'nik':result.nik,
                'email':result.email,
                'company':result.company,
                'transaction': trancation

            }
    } 