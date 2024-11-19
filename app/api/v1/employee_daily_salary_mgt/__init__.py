# app/api/v1/employee_daily_salary/__init__.py

from fastapi import APIRouter
from app.api.v1.employee_daily_salary_mgt.manage_employee_daily_salary import router as manage_employee_daily_salary_router

router = APIRouter(tags=["Employee Daily Salary Management"])
router.include_router(manage_employee_daily_salary_router)
