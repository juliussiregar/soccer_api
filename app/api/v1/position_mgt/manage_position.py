# api/v1/position_mgt/position_mgt.py

import uuid
from fastapi import APIRouter, Depends, HTTPException
from typing import Optional, Annotated
from app.schemas.position import CreateNewPosition, PositionFilter, UpdatePosition
from app.services.position import PositionService
from app.middleware.jwt import jwt_middleware, AuthUser
from app.core.constants.auth import ROLE_ADMIN, ROLE_HR

# Definisikan router
router = APIRouter()
position_service = PositionService()

@router.post('/positions', description="Create a new Position")
def create_position(
    auth_user: Annotated[AuthUser, Depends(jwt_middleware)],
    request_body: CreateNewPosition
):
    position_service.auth_service.has_role(auth_user.id, ROLE_ADMIN)
    position = position_service.create_position(request_body)
    return {
        "data": {
            "position": {
                "id": position.id,
                "company_id": position.company_id,
                "name": position.name,
                "description": position.description,
                "created_at": position.created_at
            }
        }
    }

@router.get('/positions')
def get_positions(
    auth_user: Annotated[AuthUser, Depends(jwt_middleware)],
    limit: int = 100,
    page: int = 1,
    q: Optional[str] = None
):
    # Cek apakah role pengguna adalah ADMIN atau HR
    if auth_user.roles and ROLE_ADMIN in auth_user.roles:
        _filter = PositionFilter(limit=limit, page=page, search=q)
    elif auth_user.roles and ROLE_HR in auth_user.roles:
        _filter = PositionFilter(limit=limit, page=page, search=q, company_id=auth_user.company_id)
    else:
        raise HTTPException(status_code=403, detail="Access denied for this role")

    positions, total_rows, total_pages = position_service.list_positions(_filter)

    return {
        "positions": [
            {
                "id": position.id,
                "name": position.name,
                "description": position.description,
                "created_at": position.created_at,
                "updated_at": position.updated_at,
                "company_name": position.company.name  # Menyertakan company_name
            }
            for position in positions
        ],
        "meta": {
            "limit": limit,
            "page": page,
            "total_rows": total_rows,
            "total_pages": total_pages,
        },
    }

@router.get('/positions/{position_id}')
def get_position_by_id(
    auth_user: Annotated[AuthUser, Depends(jwt_middleware)],
    position_id: int,
    company_id: uuid.UUID
):
    position_service.auth_service.has_role(auth_user.id, ROLE_ADMIN)
    position = position_service.get_position(position_id, company_id)
    if position is None:
        raise HTTPException(status_code=404, detail="Position not found")

    return {
        "data": {
            "id": position.id,
            "name": position.name,
            "description": position.description,
            "created_at": position.created_at,
            "updated_at": position.updated_at,
        }
    }

@router.put('/positions/{position_id}')
def update_position(
    auth_user: Annotated[AuthUser, Depends(jwt_middleware)],
    position_id: int,
    request_body: UpdatePosition
):
    position_service.auth_service.has_role(auth_user.id, ROLE_ADMIN)
    position = position_service.update_position(position_id, request_body)
    if position is None:
        raise HTTPException(status_code=404, detail="Position not found or could not be updated")

    return {
        "data": {
            "id": position.id,
            "name": position.name,
            "description": position.description,
            "updated_at": position.updated_at,
        }
    }

@router.delete('/positions/{position_id}')
def delete_position(
    auth_user: Annotated[AuthUser, Depends(jwt_middleware)],
    position_id: int
):
    position_service.auth_service.has_role(auth_user.id, ROLE_ADMIN)
    position = position_service.delete_position(position_id)
    if position is None:
        raise HTTPException(status_code=404, detail="Position not found")

    return {
        "data": "Position deleted successfully"
    }
