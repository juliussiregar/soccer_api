import base64
from typing import List, Tuple
from app.models.role import Role
from app.models.user import User
from app.models.face import FaceGalleries,Faces
from app.clients.face_api import FaceApiClient

from app.repositories.role import RoleRepository
# from app.repositories.faceapi import FaceApiRepository
from app.schemas.faceapi_mgt import EnrollFace

from app.utils.exception import (
    UnprocessableException,
    NotFoundException,
    InternalErrorException,
)
from app.utils.logger import logger

class FaceApiService :
    def __init__(self) -> None:
        self.client =FaceApiClient()

    def insert_face(self,payload:EnrollFace,file:str) :
        # is_facegalliries_exist = self.face_repo.is_facegalleries_used(payload.facegallery_id)
        payload.image = file
        try:
            facegallery = self.client.create_facegallery(payload)
        except Exception as err:
            err_msg = str(err)
            logger.error(err_msg)
            raise InternalErrorException(err_msg)
        
        return facegallery
    
    def encode_image(path_image:str):
        with open(path_image, "rb") as f:
            encoded_string = base64.b64encode(f.read())

        return encoded_string