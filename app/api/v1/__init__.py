# v1/__init__.py

from fastapi import APIRouter
from app.api.v1.auth import router as auth_router
from app.api.v1.user_mgt import router as user_router
from app.api.v1.position_mgt import router as position_router
from app.api.v1.company_mgt import router as company_router
from app.api.v1.employee_mgt import router as employee_router
from app.api.v1.dailySalary_mgt import router as dailySalary_router

router = APIRouter(prefix="/v1")
router.include_router(auth_router)
router.include_router(user_router)
router.include_router(position_router)
router.include_router(company_router)
router.include_router(employee_router)
router.include_router(dailySalary_router)
