import base64
import json
import requests
import time
from fastapi import HTTPException, status
from typing import Any, Dict, List, Tuple

from app.core.config import settings
from app.utils.exception import InternalErrorException
from app.utils.logger import logger
from app.schemas.faceapi_mgt import CreateEnrollFace, CreateFaceGallery, DeleteVisitor,GetEnrollFace,IdentifyFace
# from app.repository.integration import IntegrationLogRepository
# from app.schema.integration import IntegrationLogCreate
from app.core.constants.request import REQUEST_GET, REQUEST_POST
from app.utils.date import get_now


class FaceApiClient:
    def __init__(self) -> None:
        self.base_url = settings.risetai_url
        self.token = settings.risetai_token

        auth_header = f"{self.token}"

        self.headers = {
            "Content-Type": "application/json",
            "Accesstoken": auth_header,
        }


    def create_facegallery(self ,payload: CreateFaceGallery) -> CreateFaceGallery :
        url = f"{self.base_url}/risetai/face-api/facegallery/create-facegallery"
        payload_json = payload.dict()
        response = requests.post(url, json=payload_json, headers=self.headers)
        response.raise_for_status()  # Raise exception for HTTP errors
        is_ok = response.status_code != status.HTTP_200_OK

        if is_ok:
            logger.error(
                f"RISETAI - POST FaceGallery {response.status_code} : {response.content}"
            )
        else:
            body = response.json().get("risetai")
        
        if body is None:
            return None
        
        if int(body["status"]) != status.HTTP_200_OK:
            raise HTTPException(status_code=int(body["status"]), detail=body["status_message"])

        return body
    
    def get_facegallery(self):
        url = f"{self.base_url}/risetai/face-api/facegallery/my-facegalleries"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()  # Raise exception for HTTP errors
        is_ok = response.status_code != status.HTTP_200_OK

        if is_ok:
            logger.error(
                f"RISETAI - GET FaceGallery {response.status_code} : {response.content}"
            )
        else:
            body = response.json().get("risetai")
        
        if body is None:
            return None
        
        if int(body["status"]) != status.HTTP_200_OK:
            raise HTTPException(status_code=int(body["status"]), detail=body["status_message"])

        return body
    
    def create_faces(self,payload:CreateEnrollFace,file:str):
        url = f"{self.base_url}/risetai/face-api/facegallery/enroll-face"
        encoded_string = base64.b64encode(file).decode("utf-8")
        payload.image = encoded_string
        payload_json = payload.dict()
        response = requests.post(url, json=payload_json, headers=self.headers)
        response.raise_for_status()  # Raise exception for HTTP errors
        is_ok = response.status_code != status.HTTP_200_OK

        if is_ok:
            logger.error(
                f"RISETAI - POST FaceGallery {response.status_code} : {response.content}"
            )
        else:
            body = response.json().get("risetai")
        
        if body is None:
            return None
        
        if int(body["status"]) != status.HTTP_200_OK:
            raise HTTPException(status_code=int(body["status"]), detail=body["status_message"])
        return body
    
    def insert_faces_visitor(self,payload:CreateEnrollFace):
        url = f"{self.base_url}/risetai/face-api/facegallery/enroll-face"
        payload_json = payload.dict()
        response = requests.post(url, json=payload_json, headers=self.headers)
        response.raise_for_status()  # Raise exception for HTTP errors
        is_ok = response.status_code != status.HTTP_200_OK

        if is_ok:
            logger.error(
                f"RISETAI - POST FaceGallery {response.status_code} : {response.content}"
            )
        else:
            body = response.json().get("risetai")
        
        if body is None:
            return None
        
        if int(body["status"]) != status.HTTP_200_OK:
            raise HTTPException(status_code=int(body["status"]), detail=body["status_message"])
        return body ,url

    def get_listface(self,facegallery_id:str,trx_id:str):
        url = f"{self.base_url}/risetai/face-api/facegallery/list-faces"
        # payload_json = payload.dict()
        params = {"facegallery_id":facegallery_id,"trx_id":trx_id}
        response = requests.get(url,json=params, headers=self.headers)
        response.raise_for_status()  # Raise exception for HTTP errors
        is_ok = response.status_code != status.HTTP_200_OK

        if is_ok:
            logger.error(
                f"RISETAI - GET FaceGallery {response.status_code} : {response.content}"
            )
        else:
            body = response.json().get("risetai")
        
        if body is None:
            return None
        
        if int(body["status"]) != status.HTTP_200_OK:
            raise HTTPException(status_code=int(body["status"]), detail=body["status_message"])

        return body
    
    def identify_face(self,payload:IdentifyFace,file:str):
        url = f"{self.base_url}/risetai/face-api/facegallery/identify-face"
        encoded_string = base64.b64encode(file).decode("utf-8")
        payload.image = encoded_string
        payload_json = payload.dict()
        response = requests.post(url, json=payload_json, headers=self.headers)
        response.raise_for_status()  # Raise exception for HTTP errors
        is_ok = response.status_code != status.HTTP_200_OK

        if is_ok:
            logger.error(
                f"RISETAI - POST FaceGallery {response.status_code} : {response.content}"
            )
        else:
            body = response.json().get("risetai")
        
        if body is None:
            return None
        
        if int(body["status"]) != status.HTTP_200_OK:
            raise HTTPException(status_code=int(body["status"]), detail=body["status_message"])
        return body
    
    def identify_face_visitor(self,payload:IdentifyFace):
        url = f"{self.base_url}/risetai/face-api/facegallery/identify-face"
        payload_json = payload.dict()
        response = requests.post(url, json=payload_json, headers=self.headers)
        response.raise_for_status()  # Raise exception for HTTP errors
        is_ok = response.status_code != status.HTTP_200_OK
        if is_ok:
            logger.error(
                f"RISETAI - POST FaceGallery {response.status_code} : {response.content}"
            )
        else:
            body = response.json().get("risetai")
            if int(body["status"]) != status.HTTP_200_OK:
                raise HTTPException(status_code=int(body["status"]), detail=body["status_message"])
            data = body["return"]
        
        if body is None:
            return None
        
        if int(body["status"]) != status.HTTP_200_OK:
            raise HTTPException(status_code=int(body["status"]), detail=body["status_message"])
        return url,data
    
    def delete_visitor(self,payload:DeleteVisitor):
        url = f"{self.base_url}/risetai/face-api/facegallery/delete-face"
        payload_json = payload.dict()
        response = requests.post(url, json=payload_json, headers=self.headers)
        response.raise_for_status()  # Raise exception for HTTP errors
        is_ok = response.status_code != status.HTTP_200_OK
        if is_ok:
            logger.error(
                f"RISETAI - POST FaceGallery {response.status_code} : {response.content}"
            )
        else:
            body = response.json().get("risetai")
        
        if body is None:
            return None
        
        if int(body["status"]) != status.HTTP_200_OK:
            raise HTTPException(status_code=int(body["status"]), detail=body["status_message"])
        return body
    