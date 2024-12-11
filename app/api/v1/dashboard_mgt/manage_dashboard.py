from typing import Annotated, Optional
from fastapi import APIRouter, Depends, HTTPException
from fastapi.params import Query
from app.core.constants.auth import ROLE_ADMIN, ROLE_HR
from app.schemas.attendance_mgt import AttendanceFilter
from app.schemas.employee import EmployeeFilter
from app.services.attendance import AttendanceService
from app.middleware.jwt import jwt_middleware, AuthUser
from app.services.employee import EmployeeService
from app.utils.logger import logger

router = APIRouter()
attendance_service = AttendanceService()
employee_service = EmployeeService()

@router.get('/attendances-dashboard', description="List all attendances with optional filtering by company_id")
def list_attendances(
        auth_user: Annotated[AuthUser, Depends(jwt_middleware)],
        q: Optional[str] = None
):
    if auth_user.roles and ROLE_ADMIN in auth_user.roles:
        _filter = AttendanceFilter(search=q)
    elif auth_user.roles and ROLE_HR in auth_user.roles:
        _filter = AttendanceFilter(search=q, company_id=auth_user.company_id)
    else:
        raise HTTPException(status_code=403, detail="Access denied: Only ADMIN or HR roles can view attendances.")

    attendances, total_records, total_pages = attendance_service.list_attendances(_filter)
    return {
        "success": True,
        "data": [
            {
                "id": att.id,
                "employee_id": att.employee_id,
                "company_id": att.company_id,
                "check_in": att.check_in,
                "check_out": att.check_out,
                "late": att.late,
                "created_at": att.created_at
            }
            for att in attendances
        ],
        "message": "Attendances retrieved successfully",
        "code": 200
    }

@router.get('/employees-dashboard')
def get_employees(
    auth_user: Annotated[AuthUser, Depends(jwt_middleware)],
    q: Optional[str] = None
):
    if auth_user.roles and ROLE_ADMIN in auth_user.roles:
        _filter = EmployeeFilter(search=q)
    elif auth_user.roles and ROLE_HR in auth_user.roles:
        _filter = EmployeeFilter(search=q, company_id=auth_user.company_id)
    else:
        raise HTTPException(status_code=403, detail="Access denied: Only ADMIN or HR roles can view employees.")

    employees, total_rows, total_pages = employee_service.list_employees(_filter)
    return {
        "employees": [
            {
                "id": employee.id,
                "company_id": employee.company_id,
                "position_id": employee.position_id,
                "nik": employee.nik,
                "user_name": employee.user_name,
                "email": employee.email,
                "created_at": employee.created_at,
                "updated_at": employee.updated_at
            }
            for employee in employees
        ],
        "message": "Employees retrieved successfully",
        "code": 200
    }


