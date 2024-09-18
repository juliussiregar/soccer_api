import uuid
from pydantic import BaseModel
from typing import Optional


class InsertClient(BaseModel):
    client_name: str