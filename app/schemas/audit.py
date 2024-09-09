from pydantic import BaseModel
from typing import Optional, List, Tuple


class ApiLogCreate(BaseModel):
    method: str
    url: str
    req_headers: Optional[List[Tuple[str, str]]] = None
    req_body: Optional[bytes] = None
    resp_status: str
    duration: float
