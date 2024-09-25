import base64
from fastapi import  HTTPException,APIRouter, Depends, File, UploadFile
from typing import Optional, Annotated
from app.core.constants.auth import ROLE_ADMIN
from app.schemas.visitor import CreateNewVisitor,VisitorFilter,IdentifyVisitor
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
def register_visitor(
    # auth_user: Annotated[AuthUser, Depends(jwt_middleware)],
    # request_body:CreateNewVisitor=Depends(),file: UploadFile = File(...)):
    request_body : CreateNewVisitor):
    # auth_service.has_role(auth_user.id, ROLE_ADMIN)
    visitors,clients,faces,transactions,face_api= visitor_service.create_visitor(request_body)

    return {
        "data": {
            "visitor": {
                "id": visitors.id,
                "full_name": visitors.full_name,
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

@router.get('/visitors')
def get_visitors(
    # auth_user: Annotated[AuthUser, Depends(jwt_middleware)],
    limit: int = 100,
    page: int = 1,
    q: Optional[str] = None):
    # auth_service.has_role(auth_user.id, ROLE_ADMIN)
    filter = VisitorFilter(limit=limit, page=page, search=q)

    visitors, total_rows, total_pages = visitor_service.list(filter)

    return {
        "visitors": [
            {
                "id": visitor.id,
                "nik":visitor.nik,
                "full_name": visitor.full_name,
                "company_name": visitor.company,
                "born_date": visitor.born_date.strftime("%d-%m-%Y"),
                "image": [face.image_base64 for face in visitor.face],
                "created_at": visitor.created_at,
                "updated_at": visitor.updated_at,
            }
            for visitor in visitors
        ],
        "meta": {
            "limit": limit,
            "page": page,
            "total_rows": total_rows,
            "total_pages": total_pages,
        },
    }
@router.get('/get-visitor')
def get_visitorbyuser(
    # auth_user: Annotated[AuthUser, Depends(jwt_middleware)],
    username:str,nik:str):
    # auth_service.has_role(auth_user.id, ROLE_ADMIN)
    visitor,visitor_face = visitor_service.get_visitor(username,nik)

    return {
        "data": {
            "visitor": visitor,
            "visitor_face": visitor_face
        }
    }

@router.post('/identify-face-visitor')
def identify_face(
    # auth_user: Annotated[AuthUser, Depends(jwt_middleware)],
    # client_name:Optional[str]=None,
    # ,file: UploadFile = File(...)
    request_body: IdentifyVisitor
    ):
    # auth_service.has_role(auth_user.id, ROLE_ADMIN)
    result = visitor_service.identify_face_visitor(request_body)   

    return {
        'status':200,
        'message':'Visitor is Valid',
        'visitor':
            {
                'nik':result.nik,
                'fullName': result.full_name,
                "companyName": result.company,
                'address':result.address,
            }
    } 