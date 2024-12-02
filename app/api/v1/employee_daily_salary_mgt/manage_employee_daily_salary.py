# api/v1/employee_daily_salary_mgt/manage_employee_daily_salary.py

import uuid
from fastapi import APIRouter, Depends, HTTPException
from typing import Optional, Annotated
from app.schemas.employee_daily_salary import CreateNewEmployeeDailySalary, EmployeeDailySalaryFilter, UpdateEmployeeDailySalary
from app.services.employee_daily_salary import EmployeeDailySalaryService
from app.middleware.jwt import jwt_middleware, AuthUser
from app.core.constants.auth import ROLE_ADMIN, ROLE_HR
from app.services.employee import EmployeeService

router = APIRouter()
employee_daily_salary_service = EmployeeDailySalaryService()
employee_service = EmployeeService()

ACCESS_DENIED_MSG = "Access denied for this role"

@router.post('/employee-daily-salaries', description="Create a new Employee Daily Salary")
def create_employee_daily_salary(
    auth_user: Annotated[AuthUser, Depends(jwt_middleware)],
    request_body: CreateNewEmployeeDailySalary
):
    if not request_body.employee_id and not request_body.position_id:
        raise HTTPException(status_code=400, detail="employee_id must be provided")

    if ROLE_ADMIN or ROLE_HR in auth_user.roles:
        employee_id = request_body.employee_id
        if not employee_id:
            raise HTTPException(status_code=400, detail="Employee ID is required.")
    elif ROLE_HR in auth_user.roles:
        company_id = auth_user.company_id
        # Jika HR mengisi employee_id, cek apakah employee_id tersebut milik perusahaan yang sama
        if request_body.employee_id:
            employee = employee_service.get_employee(uuid.UUID(request_body.employee_id))
            if str(employee.company_id) != str(company_id):
                raise HTTPException(status_code=403, detail="Employee does not belong to your company.")
    else:
        raise HTTPException(status_code=403, detail=ACCESS_DENIED_MSG)

    employee_daily_salary = employee_daily_salary_service.create_employee_daily_salary(CreateNewEmployeeDailySalary(
        employee_id=employee_id,
        work_date=request_body.work_date,
        hours_worked=request_body.hours_worked,
        late_deduction=request_body.late_deduction,
        month=request_body.month,
        year=request_body.year,
        normal_salary=request_body.normal_salary,
        total_salary=request_body.total_salary,
    ))

    return {"data": employee_daily_salary}

@router.get('/employee-daily-salaries')
def get_employee_daily_salaries(
    auth_user: Annotated[AuthUser, Depends(jwt_middleware)],
    limit: int = 100,
    page: int = 1,
    employee_id: Optional[str] = None
):
    if auth_user.roles and ROLE_ADMIN or ROLE_HR in auth_user.roles:
        _filter = EmployeeDailySalaryFilter(limit=limit, page=page, employee_id=employee_id)
    else:
        raise HTTPException(status_code=403, detail=ACCESS_DENIED_MSG)

    employee_daily_salaries, total_rows, total_pages = employee_daily_salary_service.list_employee_daily_salaries(_filter)
    return {"data": employee_daily_salaries, "meta": {"limit": limit, "page": page, "total_rows": total_rows, "total_pages": total_pages}}

@router.get('/employee-daily-salaries/{employee_daily_salary_id}')
def get_employee_daily_salary_by_id(
    auth_user: Annotated[AuthUser, Depends(jwt_middleware)],
    employee_daily_salary_id: int
):
    if not auth_user.roles or ROLE_ADMIN or ROLE_HR not in auth_user.roles:
        raise HTTPException(
            status_code=403,
            detail=ACCESS_DENIED_MSG
        )

    employee_daily_salary = employee_daily_salary_service.get_employee_daily_salary(employee_daily_salary_id)
    if employee_daily_salary is None:
        raise HTTPException(status_code=404, detail="Employee Daily Salary not found")

    return {"data": employee_daily_salary}

@router.put('/employee-daily-salaries/{employee_daily_salary_id}')
def update_employee_daily_salary(
    auth_user: Annotated[AuthUser, Depends(jwt_middleware)],
    employee_daily_salary_id: int,
    request_body: UpdateEmployeeDailySalary
):
    employee_daily_salary = employee_daily_salary_service.get_employee_daily_salary(employee_daily_salary_id)
    if employee_daily_salary is None:
        raise HTTPException(status_code=404, detail="Employee Daily Salary not found")

    # Validasi untuk HR: pastikan daily salary milik perusahaan yang sama
    if ROLE_HR in auth_user.roles:
        company_id = auth_user.company_id
        if str(employee_daily_salary.company_id) != str(company_id):
            raise HTTPException(status_code=403, detail=ACCESS_DENIED_MSG)
    elif ROLE_ADMIN not in auth_user.roles:
        raise HTTPException(status_code=403, detail=ACCESS_DENIED_MSG)

    updated_employee_daily_salary = employee_daily_salary_service.update_employee_daily_salary(
        employee_daily_salary_id=employee_daily_salary_id,
        payload=request_body
    )
    return {"data": updated_employee_daily_salary}

@router.delete('/employee-daily-salaries/{employee_daily_salary_id}')
def delete_employee_daily_salary(
    auth_user: Annotated[AuthUser, Depends(jwt_middleware)],
    employee_daily_salary_id: int
):
    employee_daily_salary = employee_daily_salary_service.get_employee_daily_salary(employee_daily_salary_id)
    if employee_daily_salary is None:
        raise HTTPException(status_code=404, detail="Employee Daily Salary not found")

    # Validasi untuk HR: pastikan daily salary milik perusahaan yang sama
    if ROLE_HR in auth_user.roles:
        company_id = auth_user.company_id
        if str(employee_daily_salary.company_id) != str(company_id):
            raise HTTPException(status_code=403, detail=ACCESS_DENIED_MSG)
    elif ROLE_ADMIN not in auth_user.roles:
        raise HTTPException(status_code=403, detail=ACCESS_DENIED_MSG)

    employee_daily_salary_service.delete_employee_daily_salary(employee_daily_salary_id=employee_daily_salary_id)
    return {"data": "Employee Daily Salary deleted successfully"}