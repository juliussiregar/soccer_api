import base64
from typing import List, Tuple
import uuid
from app.schemas.user_mgt import UserFilter
from app.services.face import FaceService
from app.repositories.transaction import TransactionRepository
from app.schemas.visitor import CreateNewVisitor,Face,GetVisitor, IdentifyVisitor,IdentifyVisitorFace
from app.schemas.faceapi_mgt import CreateEnrollFace,IdentifyFace
from app.repositories.visitor import VisitorRepository
from app.repositories.client import ClientRepository
from app.repositories.face import FaceRepository
from app.clients.face_api import FaceApiClient
from app.models.client import Client
from app.models.visitor import Visitor
from app.models.transaction import Transaction
from app.models.face import Faces
from app.core.constants.information import CLIENT_NAME


from app.utils.exception import InternalErrorException, UnprocessableException
from app.utils.logger import logger


class VisitorService:
    def __init__(self) -> None:
        self.face_service = FaceService()
        self.visitor_repo = VisitorRepository()
        self.client_repo = ClientRepository()
        self.face_repo = FaceRepository()
        self.trx_repo = TransactionRepository()
        self.face_api_clients = FaceApiClient()

    def create_visitor(self,payload:CreateNewVisitor) -> Tuple[Client,Visitor, Faces,Transaction]:
        is_nik_exist = self.visitor_repo.is_nik_used(payload.nik)
        get_client = self.client_repo.get_client()
        payload.client_name = get_client.client_name
        split_fullname = payload.full_name.split()
        username_visitor =  f"{split_fullname[0]}"
        is_username_exist = self.visitor_repo.is_username_used(username_visitor)
      
        if get_client is None:
            raise UnprocessableException("Client not found")
        
        if is_username_exist and is_nik_exist:
            raise UnprocessableException("Username and NIK already used")
        else:
            payload.username = username_visitor
        
        if payload.client_name is None :
            payload.client_name = CLIENT_NAME
        
        
        # encoded_string = self.face_service.encode_image(file)
        # payload.image = encoded_string
    

        try :
            trx_id = uuid.uuid4()
            visitor,client,face = self.visitor_repo.insert(payload)
            enroll = CreateEnrollFace(
                user_id=str(visitor.nik),
                user_name=visitor.username,
                facegallery_id=client.client_name,
                image=payload.image,
                trx_id=str(trx_id)
            )
            face_api,url = self.face_api_clients.insert_faces_visitor(enroll)
            transaction = self.trx_repo.insert_transaction(trx_id,visitor.id,client.id,url)


        
        except Exception as err:
            err_msg = str(err)
            logger.error(err_msg)
            raise InternalErrorException(err_msg)

        return visitor,client,face,transaction,face_api
    

    def list(self,filter: UserFilter)->Tuple[Visitor,Faces]:
        visitors = self.visitor_repo.get_all_filtered(filter)

        total_rows = self.visitor_repo.count_by_filter(filter)
        total_pages = (total_rows + filter.limit - 1) // filter.limit
        return visitors, total_rows, total_pages

    def get_visitor(self,username:str,nik:str)->Tuple[Visitor,Faces]:
        visitor = self.visitor_repo.get_visitor(username,nik)
        if visitor is None:
            raise UnprocessableException("Username or NIK not found")
        visitor_id = self.visitor_repo.get_visitorid(username,nik)
        if visitor_id is None:
            raise UnprocessableException("Visitor ID not found")
        visitor_face = self.face_repo.get_face_byvisitorid(visitor_id)
        return visitor ,visitor_face
    

    def identify_face_visitor_image(self,client_name:str,file:str)->Tuple[Visitor,Faces,List[Transaction]]:
        get_client = self.client_repo.get_client()
        client_name = get_client.client_name
        if client_name is None:
            client_name = CLIENT_NAME
        client_id = self.client_repo.get_client_id(client_name)
        if client_id is None :
            raise UnprocessableException("Client not found")
        try:
            # encoded_string = self.face_service.encode_image(file)
            trx_id = uuid.uuid4()
            identify = IdentifyFace(
                facegallery_id=client_name,
                image=file,
                trx_id=str(trx_id)
            )
            url ,data = self.face_api_clients.identify_face_visitor(identify)
            user_id = data[0].get("user_id")
            
            check_visitor = self.visitor_repo.is_nik_used(user_id)
            if check_visitor :
                visitor = self.visitor_repo.get_visitor_bynik(user_id)
                transaction = self.trx_repo.insert_transaction(trx_id,visitor.id,client_id,url)
            else:
                raise UnprocessableException('VISITOR NOT VALID')
        except Exception as err:
            err_msg = str(err)
            logger.error(err_msg)
            raise InternalErrorException(err_msg)



        return visitor,transaction
    
    def identify_face_visitor(self,payload:IdentifyVisitor)->Tuple[Visitor,Faces,List[Transaction]]:
        get_client = self.client_repo.get_client()
        payload.client_name = get_client.client_name
        if payload.client_name is None:
            payload.client_name = CLIENT_NAME
        client_id = self.client_repo.get_client_id(payload.client_name)
        if client_id is None :
            raise UnprocessableException("Client not found")
        try:
            trx_id = uuid.uuid4()
            identify = IdentifyFace(
                facegallery_id=payload.client_name,
                image=payload.image,
                trx_id=str(trx_id)
            )
            url ,data = self.face_api_clients.identify_face_visitor(identify)
            user_id = data[0].get("user_id")
            
            check_visitor = self.visitor_repo.is_nik_used(user_id)
            if check_visitor :
                visitor = self.visitor_repo.get_visitor_bynik(user_id)
                transaction = self.trx_repo.insert_transaction(trx_id,visitor.id,client_id,url)
            else:
                raise UnprocessableException('VISITOR NOT VALID')
        except Exception as err:
            err_msg = str(err)
            logger.error(err_msg)
            raise InternalErrorException(err_msg)



        return visitor


    
    # def encode_image(self,path_image:str):
    #     file_content = path_image.file.read()
    #     with open(path_image.filename, "wb") as f:
    #         encoded_string = base64.b64encode(file_content)

    #     return encoded_string