from fastapi import APIRouter

from app.utils.logger import logger
from app.utils.date import get_now

router = APIRouter()


@router.get("/health")
async def health_check():
    logger.info("status: ok")
    return {"status": "ok", "date": get_now().strftime("%Y-%m-%d %H:%M:%S")}
