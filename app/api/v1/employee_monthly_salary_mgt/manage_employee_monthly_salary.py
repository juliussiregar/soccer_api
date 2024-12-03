# api/v1/employee_monthly_salary_mgt/manage_employee_monthly_salary.py

import uuid

import redis
from celery.result import AsyncResult
from fastapi import APIRouter, Depends, HTTPException
from typing import Optional, Annotated

from app.repositories.employee_daily_salary import EmployeeDailySalaryRepository
from app.repositories.employee_monthly_salary import EmployeeMonthlySalaryRepository
from app.schemas.employee_monthly_salary import CreateNewEmployeeMonthlySalary, EmployeeMonthlySalaryFilter, \
    UpdateEmployeeMonthlySalary, SalaryRequest
from app.services.employee_monthly_salary import EmployeeMonthlySalaryService
from app.middleware.jwt import jwt_middleware, AuthUser
from app.core.constants.auth import ROLE_ADMIN, ROLE_HR
from app.services.employee import EmployeeService
from app.services.employee_monthly_salary_periodic import calculate_monthly_salary_periodic

router = APIRouter()
employee_daily_salary_repo = EmployeeDailySalaryRepository()
employee_monthly_salary_repo = EmployeeMonthlySalaryRepository()
employee_monthly_salary_service = EmployeeMonthlySalaryService(employee_daily_salary_repo=employee_daily_salary_repo, employee_monthly_salary_repo=employee_monthly_salary_repo)
employee_service = EmployeeService()

ACCESS_DENIED_MSG = "Access denied for this role"

@router.post("/employee-monthly-salary/create-update-calculate")
async def create_update_monthly_salary(
        auth_user: Annotated[AuthUser, Depends(jwt_middleware)],
        request: SalaryRequest
):
    """
    Endpoint untuk membuat atau memperbarui gaji bulanan secara manual
    """
    try:
        employee_monthly_salary_service.create_or_update_monthly_salary(request.month, request.year)
        return {"message": f"Monthly salary for {request.month}/{request.year} has been calculated successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating monthly salary: {str(e)}")

@router.get('/employee-monthly-salaries')
def get_employee_monthly_salaries(
        auth_user: Annotated[AuthUser, Depends(jwt_middleware)],
        limit: int = 100,
        page: int = 1,
        employee_id: Optional[str] = None
):
    if ROLE_ADMIN in auth_user.roles or ROLE_HR in auth_user.roles:
        _filter = EmployeeMonthlySalaryFilter(limit=limit, page=page, employee_id=employee_id)
    else:
        raise HTTPException(status_code=403, detail=ACCESS_DENIED_MSG)

    employee_monthly_salaries, total_rows, total_pages = employee_monthly_salary_service.list_employee_monthly_salaries(
        _filter)
    return {"data": employee_monthly_salaries,
            "meta": {"limit": limit, "page": page, "total_rows": total_rows, "total_pages": total_pages}}


@router.get('/employee-monthly-salaries/{employee_monthly_salary_id}')
def get_employee_monthly_salary_by_id(
        auth_user: Annotated[AuthUser, Depends(jwt_middleware)],
        employee_monthly_salary_id: int
):
    if not (ROLE_ADMIN in auth_user.roles or ROLE_HR in auth_user.roles):
        raise HTTPException(status_code=403, detail=ACCESS_DENIED_MSG)

    employee_monthly_salary = employee_monthly_salary_service.get_employee_monthly_salary(employee_monthly_salary_id)
    if employee_monthly_salary is None:
        raise HTTPException(status_code=404, detail="Employee Monthly Salary not found")

    return {"data": employee_monthly_salary}


@router.put('/employee-monthly-salaries/{employee_monthly_salary_id}')
def update_employee_monthly_salary(
        auth_user: Annotated[AuthUser, Depends(jwt_middleware)],
        employee_monthly_salary_id: int,
        request_body: UpdateEmployeeMonthlySalary
):
    employee_monthly_salary = employee_monthly_salary_service.get_employee_monthly_salary(employee_monthly_salary_id)
    if employee_monthly_salary is None:
        raise HTTPException(status_code=404, detail="Employee Monthly Salary not found")

    updated_employee_monthly_salary = employee_monthly_salary_service.update_employee_monthly_salary(
        employee_monthly_salary_id=employee_monthly_salary_id,
        payload=request_body
    )
    return {"data": updated_employee_monthly_salary}


@router.delete('/employee-monthly-salaries/{employee_monthly_salary_id}')
def delete_employee_monthly_salary(
        auth_user: Annotated[AuthUser, Depends(jwt_middleware)],
        employee_monthly_salary_id: int
):
    employee_monthly_salary = employee_monthly_salary_service.get_employee_monthly_salary(employee_monthly_salary_id)
    if employee_monthly_salary is None:
        raise HTTPException(status_code=404, detail="Employee Monthly Salary not found")

    employee_monthly_salary_service.delete_employee_monthly_salary(
        employee_monthly_salary_id=employee_monthly_salary_id)
    return {"data": "Employee Monthly Salary deleted successfully"}
