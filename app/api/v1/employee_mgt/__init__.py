# app/api/v1/employee_mgt/__init__.py

from fastapi import APIRouter
from app.api.v1.employee_mgt.manage_employee import router as manage_employee_router

router = APIRouter(tags=["Employee Management"])
router.include_router(manage_employee_router)
