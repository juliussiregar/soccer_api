import uuid
from pydantic import BaseModel
from typing import List, Optional
from datetime import date, datetime



class CreateTrasaction(BaseModel):
    client_id : uuid.UUID
    visitor_id : uuid.UUID
    