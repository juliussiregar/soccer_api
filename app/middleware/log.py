import time
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.repositories.audit import ApiLogRepository
from app.schemas.audit import ApiLogCreate
from app.utils.logger import logger


class LogMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.log_repo = ApiLogRepository()

    async def dispatch(self, request: Request, call_next):
        start = time.time()

        req_body = await request.body()
        response: Response = await call_next(request)

        # Disable logging for health check
        path = str(request.url.path)
        if path == "/api/health" or path == "/api/health/":
            return response

        try:
            self.log_repo.insert(
                ApiLogCreate(
                    method=request.method,
                    url=str(request.url),
                    req_headers=request.headers.items(),
                    req_body=req_body,
                    resp_status=str(response.status_code),
                    duration=time.time() - start,
                )
            )
        except Exception as err:
            logger.warning(err)
            pass

        return response
