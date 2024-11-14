# api/v1/daily_salary_mgt/manage_daily_salary.py

import uuid
from fastapi import APIRouter, Depends, HTTPException
from typing import Optional, Annotated
from app.schemas.daily_salary import CreateNewDailySalary, DailySalaryFilter, UpdateDailySalary
from app.services.daily_salary import DailySalaryService
from app.middleware.jwt import jwt_middleware, AuthUser
from app.core.constants.auth import ROLE_ADMIN, ROLE_HR
from app.services.employee import EmployeeService
from app.services.position import PositionService

router = APIRouter()
daily_salary_service = DailySalaryService()
employee_service = EmployeeService()
position_service = PositionService()

ACCESS_DENIED_MSG = "Access denied for this role"

@router.post('/daily-salaries', description="Create a new Daily Salary")
def create_daily_salary(
    auth_user: Annotated[AuthUser, Depends(jwt_middleware)],
    request_body: CreateNewDailySalary
):
    if not request_body.employee_id and not request_body.position_id:
        raise HTTPException(status_code=400, detail="Either employee_id or position_id must be provided, but not both.")
    if request_body.employee_id and request_body.position_id:
        raise HTTPException(status_code=400, detail="Cannot provide both employee_id and position_id; select one only.")

    if ROLE_ADMIN in auth_user.roles:
        company_id = request_body.company_id
        if not company_id:
            raise HTTPException(status_code=400, detail="Company ID is required for Admin users.")
    elif ROLE_HR in auth_user.roles:
        company_id = auth_user.company_id
        # Jika HR mengisi employee_id, cek apakah employee_id tersebut milik perusahaan yang sama
        if request_body.employee_id:
            employee = employee_service.get_employee(uuid.UUID(request_body.employee_id))
            if str(employee.company_id) != str(company_id):
                raise HTTPException(status_code=403, detail="Employee does not belong to your company.")
        # Jika HR mengisi position_id, cek apakah position_id tersebut milik perusahaan yang sama
        if request_body.position_id:
            try:
                position = position_service.get_position(request_body.position_id, company_id)
            except Exception:
                raise HTTPException(status_code=404, detail="Position not found")
            if str(position.company_id) != str(company_id):
                raise HTTPException(status_code=403, detail="Position does not belong to your company.")
    else:
        raise HTTPException(status_code=403, detail=ACCESS_DENIED_MSG)

    # Lanjutkan proses pembuatan Daily Salary
    daily_salary = daily_salary_service.create_daily_salary(CreateNewDailySalary(
        company_id=company_id,
        employee_id=request_body.employee_id,
        position_id=request_body.position_id,
        hours_rate=request_body.hours_rate,
        standard_hours=request_body.standard_hours,
        max_late=request_body.max_late,
        late_deduction=request_body.late_deduction,
        min_overtime=request_body.min_overtime,
        overtime_pay=request_body.overtime_pay
    ))

    return {"data": daily_salary}

@router.get('/daily-salaries')
def get_daily_salaries(
    auth_user: Annotated[AuthUser, Depends(jwt_middleware)],
    limit: int = 100,
    page: int = 1,
    company_id: Optional[str] = None
):
    if auth_user.roles and ROLE_ADMIN in auth_user.roles:
        _filter = DailySalaryFilter(limit=limit, page=page, company_id=company_id)
    elif auth_user.roles and ROLE_HR in auth_user.roles:
        _filter = DailySalaryFilter(limit=limit, page=page, company_id=auth_user.company_id)
    else:
        raise HTTPException(status_code=403, detail=ACCESS_DENIED_MSG)

    daily_salaries, total_rows, total_pages = daily_salary_service.list_daily_salaries(_filter)
    return {"data": daily_salaries, "meta": {"limit": limit, "page": page, "total_rows": total_rows, "total_pages": total_pages}}

@router.get('/daily-salaries/{daily_salary_id}')
def get_daily_salary_by_id(
    auth_user: Annotated[AuthUser, Depends(jwt_middleware)],
    daily_salary_id: int
):
    daily_salary = daily_salary_service.get_daily_salary(daily_salary_id)
    if daily_salary is None:
        raise HTTPException(status_code=404, detail="Daily Salary not found")

    # Validasi untuk HR: pastikan daily salary milik perusahaan yang sama
    if ROLE_HR in auth_user.roles:
        company_id = auth_user.company_id
        if str(daily_salary.company_id) != str(company_id):
            raise HTTPException(status_code=403, detail=ACCESS_DENIED_MSG)
        # Cek position_id jika ada
        if daily_salary.position_id:
            try:
                position = position_service.get_position(daily_salary.position_id, company_id)
            except Exception:
                raise HTTPException(status_code=404, detail="Position not found")
            if str(position.company_id) != str(company_id):
                raise HTTPException(status_code=403, detail="Position does not belong to your company.")
    elif ROLE_ADMIN not in auth_user.roles:
        raise HTTPException(status_code=403, detail=ACCESS_DENIED_MSG)

    return {"data": daily_salary}

@router.put('/daily-salaries/{daily_salary_id}')
def update_daily_salary(
    auth_user: Annotated[AuthUser, Depends(jwt_middleware)],
    daily_salary_id: int,
    request_body: UpdateDailySalary
):
    daily_salary = daily_salary_service.get_daily_salary(daily_salary_id)
    if daily_salary is None:
        raise HTTPException(status_code=404, detail="Daily Salary not found")

    # Validasi untuk HR: pastikan daily salary milik perusahaan yang sama
    if ROLE_HR in auth_user.roles:
        company_id = auth_user.company_id
        if str(daily_salary.company_id) != str(company_id):
            raise HTTPException(status_code=403, detail=ACCESS_DENIED_MSG)
        # Validasi position_id jika akan diperbarui
        if request_body.position_id:
            try:
                position = position_service.get_position(request_body.position_id, company_id)
            except Exception:
                raise HTTPException(status_code=404, detail="Position not found")
            if str(position.company_id) != str(company_id):
                raise HTTPException(status_code=403, detail="Position does not belong to your company.")
    elif ROLE_ADMIN not in auth_user.roles:
        raise HTTPException(status_code=403, detail=ACCESS_DENIED_MSG)

    updated_daily_salary = daily_salary_service.update_daily_salary(
        daily_salary_id=daily_salary_id,
        payload=request_body
    )
    return {"data": updated_daily_salary}

@router.delete('/daily-salaries/{daily_salary_id}')
def delete_daily_salary(
    auth_user: Annotated[AuthUser, Depends(jwt_middleware)],
    daily_salary_id: int
):
    daily_salary = daily_salary_service.get_daily_salary(daily_salary_id)
    if daily_salary is None:
        raise HTTPException(status_code=404, detail="Daily Salary not found")

    # Validasi untuk HR: pastikan daily salary milik perusahaan yang sama
    if ROLE_HR in auth_user.roles:
        company_id = auth_user.company_id
        if str(daily_salary.company_id) != str(company_id):
            raise HTTPException(status_code=403, detail=ACCESS_DENIED_MSG)
        # Validasi position_id jika ada
        if daily_salary.position_id:
            try:
                position = position_service.get_position(daily_salary.position_id, company_id)
            except Exception:
                raise HTTPException(status_code=404, detail="Position not found")
            if str(position.company_id) != str(company_id):
                raise HTTPException(status_code=403, detail="Position does not belong to your company.")
    elif ROLE_ADMIN not in auth_user.roles:
        raise HTTPException(status_code=403, detail=ACCESS_DENIED_MSG)

    daily_salary_service.delete_daily_salary(daily_salary_id=daily_salary_id)
    return {"data": "Daily Salary deleted successfully"}