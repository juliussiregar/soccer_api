# import base64
# import uuid
# from fastapi import  HTTPException,APIRouter, Depends, File, UploadFile
# from typing import Optional, Annotated

# from urllib3 import request
# import logging

# logger = logging.getLogger(__name__)
# logger.setLevel(logging.INFO)

# from app.core.constants.auth import ROLE_ADMIN
# from app.schemas.visitor import CreateNewVisitor,VisitorFilter,IdentifyVisitor
# from app.schemas.faceapi_mgt import CreateEnrollFace,GetEnrollFace,IdentifyFace

# from app.clients.face_api import FaceApiClient
# from app.services.attendance_local import AttendanceLocalService
# from app.services.auth import AuthService
# # from app.services.face_api import FaceApiService
# from app.services.visitor import VisitorService
# from app.middleware.jwt import jwt_middleware, AuthUser

# client = FaceApiClient()
# router = APIRouter()
# auth_service = AuthService()
# visitor_service = VisitorService()
# attendance_local_service = AttendanceLocalService()


# @router.post('/register/visitor' ,description="Create new Visitor With Upload Picture")
# def register_visitor(
#     # auth_user: Annotated[AuthUser, Depends(jwt_middleware)],
#     # request_body:CreateNewVisitor=Depends(),file: UploadFile = File(...)):
#     request_body : CreateNewVisitor):
#     # auth_service.has_role(auth_user.id, ROLE_ADMIN)
#     visitors,clients,faces,transactions,face_api= visitor_service.create_visitor(request_body)

#     return {
#         "data": {
#             "visitor": {
#                 "id": visitors.id,
#                 "full_name": visitors.full_name,
#                 "username": visitors.username,
#                 "nik": visitors.nik,
#                 "born_date": visitors.born_date,
#                 "email": visitors.email,
#                 "company_name": visitors.company,
#                 "client_id":visitors.client_id,
#                 "created_at": visitors.created_at
#             },
#             "client": {
#                 "id": clients.id,
#                 "client_name": clients.client_name,
#                 "created_at": clients.created_at
#             },
#             "face": {
#                 "id": faces.id,
#                 "visitor_id": faces.visitor_id,
#                 "client_id": faces.client_id,
#                 "created_at": faces.created_at
#             },
#             "transaction": {
#                 "trx_id": transactions.id,
#                 "client_id": transactions.client_id,
#                 "visitor_id":transactions.visitor_id
#             },
#             "Riset-AI":face_api
            
#         }
#     }

# @router.get('/visitors')
# def get_visitors(
#     # auth_user: Annotated[AuthUser, Depends(jwt_middleware)],
#     limit: int = 100,
#     page: int = 1,
#     q: Optional[str] = None):
#     # auth_service.has_role(auth_user.id, ROLE_ADMIN)
#     filter = VisitorFilter(limit=limit, page=page, search=q)

#     visitors, total_rows, total_pages = visitor_service.list(filter)

#     return {
#         "visitors": [
#             {
#                 "id": visitor.id,
#                 "nik":visitor.nik,
#                 "full_name": visitor.full_name,
#                 "company_name": visitor.company,
#                 "born_date": visitor.born_date.strftime("%d-%m-%Y"),
#                 "image": [face.image_base64 for face in visitor.face],
#                 "created_at": visitor.created_at,
#                 "updated_at": visitor.updated_at,
#             }
#             for visitor in visitors
#         ],
#         "meta": {
#             "limit": limit,
#             "page": page,
#             "total_rows": total_rows,
#             "total_pages": total_pages,
#         },
#     }
# @router.get('/get-visitor')
# def get_visitorbyuser(
#     # auth_user: Annotated[AuthUser, Depends(jwt_middleware)],
#     username:str,nik:str):
#     # auth_service.has_role(auth_user.id, ROLE_ADMIN)
#     visitor,visitor_face = visitor_service.get_visitor(username,nik)

#     return {
#         "data": {
#             "visitor": visitor,
#             "visitor_face": visitor_face
#         }
#     }

# @router.post('/identify-face-visitor')
# def identify_face(
#     # auth_user: Annotated[AuthUser, Depends(jwt_middleware)],
#     # client_name:Optional[str]=None,
#     # ,file: UploadFile = File(...)
#     request_body: IdentifyVisitor
#     ):
#     # auth_service.has_role(auth_user.id, ROLE_ADMIN)
#     try:
#         # First try to create attendance
#         logger.info("Attempting to create attendance...")
#         new_attendance, visitor_info = attendance_local_service.create(request_body)

#         logger.info("Successfully created attendance")
#         return {
#             'status': 200,
#             'message': 'Visitor is Valid by Local',
#             'visitor': {
#                 'nik': visitor_info.get('nik', ''),
#                 'fullName': visitor_info.get('full_name', ''),
#                 'companyName': visitor_info.get('company', ''),
#                 'address': visitor_info.get('address', ''),
#             }
#         }

#     except HTTPException as e:
#         logger.info(f"Initial attendance creation failed with status {e.status_code}")

#         if e.status_code in [404]:  # No matching face
#             # Fall back to identify_face_visitor
#             try:
#                 logger.info("Attempting fallback to identify_face_visitor...")
#                 visitor = visitor_service.identify_face_visitor(request_body)

#                 logger.info("Successfully identified visitor through fallback method")
#                 return {
#                     'status': 200,
#                     'message': 'Visitor is Valid',
#                     'visitor': {
#                         'nik': visitor.nik,
#                         'fullName': visitor.full_name,
#                         'companyName': visitor.company,
#                         'address': visitor.address,
#                     }
#                 }

#             except Exception as identify_err:
#                 logger.error(f"Fallback identification failed: {str(identify_err)}")
#                 raise HTTPException(
#                     status_code=400,
#                     detail=f"Both identification methods failed: {str(identify_err)}"
#                 )
#         else:
#             # Re-raise other HTTP exceptions
#             logger.error(f"Non-fallback HTTP error occurred: {str(e)}")
#             raise

#     except Exception as e:
#         # Handle any other unexpected errors
#         logger.error(f"Unexpected error in identify_face: {str(e)}")
#         raise HTTPException(
#             status_code=500,
#             detail=f"An unexpected error occurred: {str(e)}"
#         )

# @router.delete('/visitors/{id}')
# def delete_visitor(
#     # auth_user: Annotated[AuthUser, Depends(jwt_middleware)],
#     id: uuid.UUID):
#     # auth_service.has_role(auth_user.id, ROLE_ADMIN)
#     visitors = visitor_service.delete_visitor(id)

#     return {
#         "data": "Deleted Success"
#     }