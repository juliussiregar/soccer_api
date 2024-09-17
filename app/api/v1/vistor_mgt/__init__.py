from fastapi import APIRouter

from app.api.v1.vistor_mgt import manage_visitor


router = APIRouter(tags=["Visitor Management"])

router.include_router(manage_visitor.router)
