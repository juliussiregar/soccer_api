from pydantic import BaseModel
from typing import Optional


class CreateFaceGallery(BaseModel):
    client_name: str
    trx_id: Optional[str] = None 


class EnrollFace(BaseModel):
    user_id: str
    user_name:str
    facegallery_id:str
    trx_id:Optional[str] = None

class CreateEnrollFace(BaseModel):
    user_id: str
    user_name: str
    facegallery_id: str
    image: Optional[str] = None  # Field ini akan di-update dengan base64 nanti
    trx_id: Optional[str] = None

class GetEnrollFace:
    facegallery_id: str
    trx_id: Optional[str] = None

class VerifyFace(BaseModel):
    user_id: str
    user_name:str
    facegallery_id:str
    image:str
    trx_id:Optional[str] = None

class IdentifyFace(BaseModel):
    facegallery_id:str
    image: Optional[str] = None
    trx_id:Optional[str] = None

class CompareImage(BaseModel):
    source_image:str
    target_image:str
    trx_id:Optional[str] = None
    