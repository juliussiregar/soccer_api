# api/v1/application_mgt/manage_application.py

from datetime import datetime, timedelta
import uuid
from fastapi import APIRouter, Depends, HTTPException
from typing import Optional, Annotated
from app.schemas.application import CreateNewApplication, ApplicationFilter, UpdateApplication,CreateWFHNewApplication
from app.services.application import ApplicationService
from app.middleware.jwt import jwt_middleware, AuthUser
from app.core.constants.auth import ROLE_ADMIN, ROLE_HR
from app.services.employee import EmployeeService
from jose import jwt, JWTError, ExpiredSignatureError
from app.core.config import settings
from app.core.database import get_session
from app.repositories.token import TokenRepository

router = APIRouter()
application_service = ApplicationService()
employee_service = EmployeeService()
revoked_tokens = set()

ACCESS_DENIED_MSG = "Access denied for this role"

@router.post('/applications', description="Create a new Application")
def create_application(
    request_body: CreateNewApplication
):
    employee = employee_service.get_employee(uuid.UUID(request_body.employee_id))
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    application = application_service.create_application(CreateNewApplication(
        employee_id=request_body.employee_id,
        location=request_body.location,
        description=request_body.description
    ))

    return {"data": application}

@router.post('/applications/wfh', description="Create a new WFH Application")
def create_wfh_application(
    request_body: CreateWFHNewApplication,
    company_id: uuid.UUID
):
    """
    Endpoint untuk membuat WFH Application dan menandai token lama sebagai revoked.
    """
    # Validasi keberadaan employee
    employee = employee_service.get_employee(uuid.UUID(request_body.employee_id))
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    # Buat aplikasi baru
    application = application_service.create_application(CreateWFHNewApplication(
        company_id=company_id,
        employee_id=request_body.employee_id,
        location=request_body.location,
        description=request_body.description
    ))

    return {
        "data": application,
        "message": "WFH application created successfully."
    }


@router.get('/applications')
def get_applications(
    auth_user: Annotated[AuthUser, Depends(jwt_middleware)],
    limit: int = 100,
    page: int = 1,
    employee_id: Optional[str] = None
):
    if auth_user.roles and ROLE_ADMIN in auth_user.roles:
        _filter = ApplicationFilter(limit=limit, page=page, employee_id=employee_id)
    elif auth_user.roles and ROLE_HR in auth_user.roles:
        # Hanya menampilkan aplikasi yang sesuai dengan company_id HR
        _filter = ApplicationFilter(limit=limit, page=page, employee_id=employee_id, company_id=auth_user.company_id)
    else:
        raise HTTPException(status_code=403, detail=ACCESS_DENIED_MSG)

    applications, total_rows, total_pages = application_service.list_applications(_filter)
    return {"data": applications, "meta": {"limit": limit, "page": page, "total_rows": total_rows, "total_pages": total_pages}}


@router.get('/applications/{application_id}')
def get_application_by_id(
    auth_user: Annotated[AuthUser, Depends(jwt_middleware)],
    application_id: int
):
    application = application_service.get_application(application_id)
    if application is None:
        raise HTTPException(status_code=404, detail="Application not found")

    # Pastikan HR hanya dapat melihat aplikasi dari company_id yang sama
    if ROLE_HR in auth_user.roles:
        employee = employee_service.get_employee(application.employee_id)  # Hapus uuid.UUID() di sini
        if str(employee.company_id) != str(auth_user.company_id):
            raise HTTPException(status_code=403, detail=ACCESS_DENIED_MSG)
    elif ROLE_ADMIN not in auth_user.roles:
        raise HTTPException(status_code=403, detail=ACCESS_DENIED_MSG)

    return {"data": application}

@router.put('/applications/{application_id}')
def update_application(
    auth_user: Annotated[AuthUser, Depends(jwt_middleware)],
    application_id: int,
    request_body: UpdateApplication
):
    application = application_service.get_application(application_id)
    if application is None:
        raise HTTPException(status_code=404, detail="Application not found")

    # Pastikan HR hanya dapat mengubah aplikasi dari company_id yang sama
    if ROLE_HR in auth_user.roles:
        employee = employee_service.get_employee(application.employee_id)  # Hapus uuid.UUID() di sini
        if str(employee.company_id) != str(auth_user.company_id):
            raise HTTPException(status_code=403, detail=ACCESS_DENIED_MSG)
    elif ROLE_ADMIN not in auth_user.roles:
        raise HTTPException(status_code=403, detail=ACCESS_DENIED_MSG)

    updated_application = application_service.update_application(
        application_id=application_id,
        payload=request_body
    )
    return {"data": updated_application}

@router.delete('/applications/{application_id}')
def delete_application(
    auth_user: Annotated[AuthUser, Depends(jwt_middleware)],
    application_id: int
):
    application = application_service.get_application(application_id)
    if application is None:
        raise HTTPException(status_code=404, detail="Application not found")

    # Pastikan HR hanya dapat menghapus aplikasi dari company_id yang sama
    if ROLE_HR in auth_user.roles:
        employee = employee_service.get_employee(application.employee_id)  # Hapus uuid.UUID() di sini
        if str(employee.company_id) != str(auth_user.company_id):
            raise HTTPException(status_code=403, detail=ACCESS_DENIED_MSG)
    elif ROLE_ADMIN not in auth_user.roles:
        raise HTTPException(status_code=403, detail=ACCESS_DENIED_MSG)

    application_service.delete_application(application_id=application_id)
    return {"data": "Application deleted successfully"}
