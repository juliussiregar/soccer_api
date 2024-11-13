from fastapi import APIRouter

from app.api.v1.company_mgt import manage_company

router = APIRouter(tags=["Company Management"])

router.include_router(manage_company.router)
