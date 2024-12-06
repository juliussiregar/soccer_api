# api/v1/employee_mgt/manage_employee.py

import uuid
from fastapi import APIRouter, Depends, HTTPException
from typing import Optional, Annotated
from app.schemas.employee import CreateNewEmployee, EmployeeFilter, UpdateEmployee
from app.services.employee import EmployeeService
from app.middleware.jwt import jwt_middleware, AuthUser
from app.core.constants.auth import ROLE_ADMIN, ROLE_HR

router = APIRouter()
employee_service = EmployeeService()

ACCESS_DENIED_MSG = "Access denied for this role"

@router.post('/employees', description="Create a new Employee")
def create_employee(
    auth_user: Annotated[AuthUser, Depends(jwt_middleware)],
    request_body: CreateNewEmployee
):
    if ROLE_ADMIN in auth_user.roles:
        company_id = request_body.company_id
        if not company_id:
            raise HTTPException(status_code=400, detail="Company ID is required for Admin users.")
    elif ROLE_HR in auth_user.roles:
        company_id = auth_user.company_id
    else:
        raise HTTPException(status_code=403, detail=ACCESS_DENIED_MSG)

    employee = employee_service.create_employee(CreateNewEmployee(
        company_id=company_id,
        position_id=request_body.position_id,
        user_name=request_body.user_name,
        nik=request_body.nik,
        email=request_body.email,
        photo=request_body.photo
    ))

    return {"data": employee}


@router.get('/employees')
def get_employees(
    auth_user: Annotated[AuthUser, Depends(jwt_middleware)],
    limit: int = 100,
    page: int = 1,
    q: Optional[str] = None
):
    if auth_user.roles and ROLE_ADMIN in auth_user.roles:
        _filter = EmployeeFilter(limit=limit, page=page, search=q)
    elif auth_user.roles and ROLE_HR in auth_user.roles:
        _filter = EmployeeFilter(limit=limit, page=page, search=q, company_id=auth_user.company_id)
    else:
        raise HTTPException(status_code=403, detail=ACCESS_DENIED_MSG)

    employees, total_rows, total_pages = employee_service.list_employees(_filter)
    return {"employees": employees, "meta": {"limit": limit, "page": page, "total_rows": total_rows, "total_pages": total_pages}}

@router.get('/employees/{employee_id}')
def get_employee_by_id(
    auth_user: Annotated[AuthUser, Depends(jwt_middleware)],
    employee_id: uuid.UUID
):
    employee = employee_service.get_employee(employee_id)
    if employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")

    if ROLE_HR in auth_user.roles and str(employee.company_id) != str(auth_user.company_id):
        raise HTTPException(status_code=403, detail=ACCESS_DENIED_MSG)

    return {"data": employee}

@router.get('/employees/{company_id}')
def get_employees_by_company_id(
    company_id: uuid.UUID
):
    employee = employee_service.get_employees_by_company_id(company_id)
    if employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")

    return {"data": employee}

@router.put('/employees/{employee_id}')
def update_employee(
    auth_user: Annotated[AuthUser, Depends(jwt_middleware)],
    employee_id: uuid.UUID,
    request_body: UpdateEmployee
):
    employee = employee_service.get_employee(employee_id)
    if employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")

    if ROLE_HR in auth_user.roles and str(employee.company_id) != str(auth_user.company_id):
        raise HTTPException(status_code=403, detail=ACCESS_DENIED_MSG)

    updated_employee = employee_service.update_employee(
        employee_id=employee_id,
        payload=request_body
    )
    return {"data": updated_employee}


@router.delete('/employees/{employee_id}')
def delete_employee(
    auth_user: Annotated[AuthUser, Depends(jwt_middleware)],
    employee_id: uuid.UUID
):
    employee = employee_service.get_employee(employee_id)
    if employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")

    # Convert to string for consistent comparison
    if ROLE_HR in auth_user.roles and str(employee.company_id) != str(auth_user.company_id):
        raise HTTPException(status_code=403, detail=ACCESS_DENIED_MSG)

    employee_service.delete_employee(employee_id=employee_id)
    return {"data": "Employee deleted successfully"}
