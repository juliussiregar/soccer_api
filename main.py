from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.middleware.log import LogMiddleware
from app.utils.exception import CustomException

from app.api.test import router as router_health
from app.api.v1 import router as v1_router

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    openapi_url="/api/openapi.json",
    description=settings.app_desc,
)


@app.exception_handler(CustomException)
def custom_exception_handler(request: Request, exc: CustomException):
    return JSONResponse(status_code=exc.status, content={"detail": exc.message})


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(LogMiddleware)

app.include_router(router_health, prefix="/api")
app.include_router(v1_router, prefix="/api")
