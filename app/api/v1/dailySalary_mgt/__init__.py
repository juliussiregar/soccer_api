# app/api/v1/employee_mgt/__init__.py

from fastapi import APIRouter
from app.api.v1.dailySalary_mgt.manage_dailySalary import router as manage_dailySalary_router

router = APIRouter(tags=["Daily Salary Management"])
router.include_router(manage_dailySalary_router)
