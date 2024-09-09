import json

from app.core.database import get_session
from app.models.audit import ApiLog
from app.schemas.audit import ApiLogCreate


class ApiLogRepository:
    def insert(self, payload: ApiLogCreate) -> ApiLog:
        log = ApiLog()

        log.method = payload.method
        log.url = payload.url
        log.resp_status = payload.resp_status
        log.duration = payload.duration

        if payload.req_headers is not None:
            log.req_headers = payload.req_headers

        if payload.req_body is not None and payload.req_body != b"":
            log.req_body = json.loads(payload.req_body)

        with get_session() as db:
            db.add(log)
            db.commit()

            db.refresh(log)

        return log
