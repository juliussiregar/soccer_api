from pydantic import BaseModel
from typing import Optional


class CreateNewVisitor(BaseModel):
    username: str
    nik : str
    client:str
    image : Optional[str] = None