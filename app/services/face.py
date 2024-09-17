import base64
from typing import List, Tuple
from app.schemas.visitor import CreateNewVisitor,Face
from app.schemas.faceapi_mgt import CreateEnrollFace
from app.repositories.visitor import VisitorRepository
from app.clients.face_api import FaceApiClient
from app.models.client import Client
from app.models.visitor import Visitor
from app.models.transaction import Transaction
from app.models.face import Faces
from app.core.constants.information import CLIENT_NAME


from app.utils.exception import InternalErrorException, UnprocessableException
from app.utils.logger import logger

class FaceService:
     def encode_image(self,path_image:str):
        file_content = path_image.file.read()
        with open(path_image.filename, "wb") as f:
            encoded_string = base64.b64encode(file_content)

        return encoded_string