# app/api/v1/employee_mgt/__init__.py

from fastapi import APIRouter
from app.api.v1.application_mgt.manage_application import router as manage_application_router

router = APIRouter(tags=["Application Management"])
router.include_router(manage_application_router)
