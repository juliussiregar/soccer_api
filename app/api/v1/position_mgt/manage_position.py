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
    # Cek role pengguna
    if ROLE_ADMIN in auth_user.roles:
        # Jika admin, gunakan company_id dari input jika ada
        company_id = request_body.company_id
        if not company_id:
            raise HTTPException(status_code=400, detail="Company ID is required for Admin users.")
    elif ROLE_HR in auth_user.roles:
        # Jika HR, set company_id secara otomatis dari auth_user
        company_id = auth_user.company_id
    else:
        # Jika bukan ADMIN atau HR, akses ditolak
        raise HTTPException(status_code=403, detail="Access denied for this role")

    # Menggunakan company_id yang sudah disesuaikan untuk membuat posisi baru
    position = position_service.create_position(CreateNewPosition(
        company_id=company_id,
        name=request_body.name,
        description=request_body.description
    ))

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
                "company_id": position.company_id,
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
    company_id: Optional[uuid.UUID] = None  # Parameter `company_id` opsional di Swagger
):
    # Validasi `company_id` berdasarkan peran pengguna
    if ROLE_ADMIN in auth_user.roles:
        # Jika Admin, `company_id` harus disertakan
        if not company_id:
            raise HTTPException(status_code=400, detail="Company ID is required for Admin users.")
    elif ROLE_HR in auth_user.roles:
        # Jika HR, gunakan `company_id` dari token pengguna
        company_id = auth_user.company_id
    else:
        # Akses ditolak jika bukan Admin atau HR
        raise HTTPException(status_code=403, detail="Access denied for this role")

    # Panggil service untuk mendapatkan posisi berdasarkan ID dan company_id
    position = position_service.get_position(position_id, company_id)
    if position is None:
        raise HTTPException(status_code=404, detail="Position not found")

    return {
        "data": {
            "id": position.id,
            "company_id": position.company_id,
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
    request_body: UpdatePosition,
    company_id: Optional[str] = None  # Tambahkan parameter company_id di sini
):
    # Validasi company_id
    if ROLE_ADMIN in auth_user.roles:
        # Admin bebas memilih company_id, jika tidak diberikan, raise error
        if not company_id:
            raise HTTPException(status_code=400, detail="Company ID is required for update.")
    elif ROLE_HR in auth_user.roles:
        # HR hanya dapat menggunakan company_id mereka sendiri
        company_id = auth_user.company_id
    else:
        # Akses ditolak jika bukan ADMIN atau HR
        raise HTTPException(status_code=403, detail="Access denied for this role")

    # Pastikan untuk meneruskan company_id dalam pembaruan posisi
    position = position_service.update_position(
        position_id=position_id,
        payload=UpdatePosition(name=request_body.name, description=request_body.description),
        company_id=company_id
    )
    if position is None:
        raise HTTPException(status_code=404, detail="Position not found or could not be updated")

    return {
        "data": {
            "id": position.id,
            "company_id": position.company_id,
            "name": position.name,
            "description": position.description,
            "updated_at": position.updated_at,
        }
    }

@router.delete('/positions/{position_id}')
def delete_position(
    auth_user: Annotated[AuthUser, Depends(jwt_middleware)],
    position_id: int,
    company_id: Optional[str] = None  # Tambahkan parameter company_id di sini
):
    # Validasi company_id
    if ROLE_ADMIN in auth_user.roles:
        # Admin bebas memilih company_id, jika tidak diberikan, raise error
        if not company_id:
            raise HTTPException(status_code=400, detail="Company ID is required for deletion.")
    elif ROLE_HR in auth_user.roles:
        # HR hanya dapat menggunakan company_id mereka sendiri
        company_id = auth_user.company_id
    else:
        # Akses ditolak jika bukan ADMIN atau HR
        raise HTTPException(status_code=403, detail="Access denied for this role")

    # Hapus posisi dengan memeriksa company_id
    position = position_service.delete_position(position_id=position_id, company_id=company_id)
    if position is None:
        raise HTTPException(status_code=404, detail="Position not found")

    return {"data": "Position deleted successfully"}