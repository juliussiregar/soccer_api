from fastapi import APIRouter

from app.utils.logger import logger
from app.utils.date import get_now

router = APIRouter()


@router.get("/test")
async def test():
    logger.info("status: ok")
    return {"status": "ok jalan mas bro", "date": get_now().strftime("%Y-%m-%d %H:%M:%S")}
