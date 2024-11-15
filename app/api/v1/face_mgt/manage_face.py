import uuid
from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional, Annotated
from app.schemas.face_mgt import CreateFace, UpdateFace, FaceData
from app.services.face import FaceService
from app.middleware.jwt import jwt_middleware, AuthUser
from app.core.constants.auth import ROLE_ADMIN, ROLE_HR

router = APIRouter()
face_service = FaceService()

@router.get('/faces/{face_id}', description="Retrieve a face by ID")
def get_face(
    face_id: uuid.UUID,
    auth_user: Annotated[AuthUser, Depends(jwt_middleware)]
):
    if not auth_user.roles or (ROLE_ADMIN not in auth_user.roles and ROLE_HR not in auth_user.roles):
        raise HTTPException(status_code=403, detail="Access denied: Only ADMIN and HR roles can access faces.")

    face = face_service.get_face(face_id)
    if not face:
        raise HTTPException(status_code=404, detail="Face not found")

    return {
        "success": True,
        "data": face,
        "message": "Face retrieved successfully",
        "code": 200
    }

@router.get('/faces', description="List all faces for a specific company")
def list_faces(
    auth_user: Annotated[AuthUser, Depends(jwt_middleware)],
    company_id: Optional[uuid.UUID] = None,
    limit: int = 10,
    page: int = 1
):
    # Check if the user has the required roles
    if not auth_user.roles or (ROLE_ADMIN not in auth_user.roles and ROLE_HR not in auth_user.roles):
        raise HTTPException(status_code=403, detail="Access denied: Only ADMIN and HR roles can access faces list.")

    # Fetch faces, total records, and total pages
    faces, total_records, total_pages = face_service.list_faces(company_id, limit, page)

    # Prepare response data
    response_data = [
        {
            "id": face.id,
            "company_id": face.company_id,
            "employee_id": face.employee_id,
            "photo": face.photo,
            "created_at": face.created_at,
            "updated_at": face.updated_at,
        }
        for face in faces
    ]

    return {
        "success": True,
        "data": response_data,
        "message": "Faces retrieved successfully",
        "code": 200,
        "meta": {
            "limit": limit,
            "page": page,
            "total_records": total_records,
            "total_pages": total_pages
        }
    }



@router.post('/faces', description="Create a new face entry")
def create_face(
    payload: CreateFace,
    auth_user: Annotated[AuthUser, Depends(jwt_middleware)]
):
    # Check if the user has the required roles
    if not auth_user.roles or (ROLE_ADMIN not in auth_user.roles and ROLE_HR not in auth_user.roles):
        raise HTTPException(status_code=403, detail="Access denied: Only ADMIN and HR roles can create a face.")

    # Unpack the returned tuple from the service method
    face, face_api_response = face_service.create_face(payload)

    return {
        "success": True,
        "data": {
            "face": {
                "id": face.id,
                "company_id": face.company_id,
                "employee_id": face.employee_id,
                "photo": face.photo,
                "created_at": face.created_at,
                "updated_at": face.updated_at,
            },
            "face_api_response": face_api_response
        },
        "message": "Face created successfully",
        "code": 201
    }


@router.put('/faces/{face_id}', description="Update a face entry by ID")
def update_face(
    face_id: uuid.UUID,
    payload: UpdateFace,
    auth_user: Annotated[AuthUser, Depends(jwt_middleware)]
):
    # Check if the user has the required roles
    if not auth_user.roles or (ROLE_ADMIN not in auth_user.roles and ROLE_HR not in auth_user.roles):
        raise HTTPException(status_code=403, detail="Access denied: Only ADMIN and HR roles can update a face.")

    face = face_service.update_face(face_id, payload)
    if not face:
        raise HTTPException(status_code=404, detail="Face not found or could not be updated")

    return {
        "success": True,
        "data": face,
        "message": "Face updated successfully",
        "code": 200
    }

@router.delete('/faces/{face_id}', description="Delete a face entry by ID")
def delete_face(
    face_id: uuid.UUID,
    auth_user: Annotated[AuthUser, Depends(jwt_middleware)]
):
    # Check if the user has the required roles
    if not auth_user.roles or (ROLE_ADMIN not in auth_user.roles and ROLE_HR not in auth_user.roles):
        raise HTTPException(status_code=403, detail="Access denied: Only ADMIN and HR roles can delete a face.")

    face = face_service.delete_face(face_id)
    if not face:
        raise HTTPException(status_code=404, detail="Face not found")

    return {
        "success": True,
        "data": None,
        "message": "Face deleted successfully",
        "code": 200
    }
