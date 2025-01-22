from fastapi import APIRouter, Depends, HTTPException
from typing import Optional, Annotated
from app.schemas.guardian import GuardianCreate, GuardianUpdate
from app.middleware.jwt import jwt_middleware, AuthUser
from app.core.constants.auth import ROLE_GUARDIAN
from app.services.guardian import GuardianService

router = APIRouter()
guardian_service = GuardianService()

@router.get("/admin/guardians", description="List all guardians (ADMIN only)")
def list_all_guardians(
    auth_user: Annotated[AuthUser, Depends(jwt_middleware)],
    limit: int = 20,
    page: int = 1,
    q: Optional[str] = None,
):
    # Check if the user has the 'ADMIN' role
    if not auth_user.roles or "ADMIN" not in auth_user.roles:
        raise HTTPException(
            status_code=403,
            detail="Access denied: Only ADMIN role can view all guardians."
        )

    try:
        guardians, total = guardian_service.list_all(limit=limit, page=page, search=q)
        total_pages = (total + limit - 1) // limit  # Calculate total pages

        return {
            "data": [
                {
                    "id": guardian.id,
                    "name": guardian.name,
                    "kartu_keluarga": guardian.kartu_keluarga,
                    "ktp": guardian.ktp,
                    "created_at": guardian.created_at,
                    "updated_at": guardian.updated_at,
                }
                for guardian in guardians
            ],
            "meta": {
                "limit": limit,
                "page": page,
                "total_rows": total,
                "total_pages": total_pages,
            },
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/guardian", description="Create a guardian profile")
def create_guardian(
    auth_user: Annotated[AuthUser, Depends(jwt_middleware)],
    body: GuardianCreate,
):
    # Check if the user has the 'GUARDIAN' role
    if not auth_user.roles or ROLE_GUARDIAN not in auth_user.roles:
        raise HTTPException(
            status_code=403,
            detail="Access denied: Only GUARDIAN role can create a guardian profile."
        )

    try:
        payload = body.dict()
        payload["user_id"] = auth_user.id  # Associate the logged-in user
        guardian = guardian_service.create(payload)
        return {
            "data": {
                "id": guardian.id,
                "name": guardian.name,
                "kartu_keluarga": guardian.kartu_keluarga,
                "ktp": guardian.ktp,
                "created_at": guardian.created_at,
                "updated_at": guardian.updated_at,
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/guardian-me", description="Get the logged-in guardian profile")
def get_guardian(auth_user: Annotated[AuthUser, Depends(jwt_middleware)]):
    # Check if the user has the 'GUARDIAN' role
    if not auth_user.roles or ROLE_GUARDIAN not in auth_user.roles:
        raise HTTPException(
            status_code=403,
            detail="Access denied: Only GUARDIAN role can view the guardian profile."
        )

    try:
        guardian = guardian_service.find_by_user_id(auth_user.id)
        if not guardian:
            raise HTTPException(status_code=404, detail="Guardian profile not found.")

        return {
            "data": {
                "id": guardian.id,
                "name": guardian.name,
                "kartu_keluarga": guardian.kartu_keluarga,
                "ktp": guardian.ktp,
                "created_at": guardian.created_at,
                "updated_at": guardian.updated_at,
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/guardian", description="Update the logged-in guardian profile")
def update_guardian(
    auth_user: Annotated[AuthUser, Depends(jwt_middleware)],
    body: GuardianUpdate,
):
    # Check if the user has the 'GUARDIAN' role
    if not auth_user.roles or ROLE_GUARDIAN not in auth_user.roles:
        raise HTTPException(
            status_code=403,
            detail="Access denied: Only GUARDIAN role can update the guardian profile."
        )

    try:
        payload = body.dict(exclude_unset=True)  # Only include fields provided in the request
        guardian = guardian_service.update(auth_user.id, payload)
        return {
            "data": {
                "id": guardian.id,
                "name": guardian.name,
                "kartu_keluarga": guardian.kartu_keluarga,
                "ktp": guardian.ktp,
                "created_at": guardian.created_at,
                "updated_at": guardian.updated_at,
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/guardian", description="Delete the logged-in guardian profile")
def delete_guardian(auth_user: Annotated[AuthUser, Depends(jwt_middleware)]):
    # Check if the user has the 'GUARDIAN' role
    if not auth_user.roles or ROLE_GUARDIAN not in auth_user.roles:
        raise HTTPException(
            status_code=403,
            detail="Access denied: Only GUARDIAN role can delete the guardian profile."
        )

    try:
        guardian_service.delete(auth_user.id)
        return {"message": "Guardian profile deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
