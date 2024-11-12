# import base64
# from typing import List, Tuple
# from app.models.role import Role
# from app.models.user import User
# # from app.models.face import Faces
# from app.models.company import Client
# from app.clients.face_api import FaceApiClient
# from app.schemas.faceapi_mgt import CreateFaceGallery

# from app.repositories.role import RoleRepository
# from app.repositories.client import ClientRepository
# from app.schemas.faceapi_mgt import EnrollFace

# from app.utils.exception import (
#     UnprocessableException,
#     NotFoundException,
#     InternalErrorException,
# )
# from app.utils.logger import logger

# class ClientService :
#     def __init__(self) -> None:
#         self.clients =FaceApiClient()
#         self.client_repo =ClientRepository()

#     def insert_facegallery(self,client_name:str)->Client:
#         is_facegalleries_exist = self.client_repo.is_facegalleries_used(client_name)
#         if is_facegalleries_exist: 
#             raise UnprocessableException("Client already Exists")
#         try:
#             client = self.client_repo.insert(client_name)
#             if client:
#                 payload = CreateFaceGallery(facegallery_id=client_name,trx_id=str(client.id))
#                 facegallery = self.clients.create_facegallery(payload)            
#         except Exception as err:
#             err_msg = str(err)
#             logger.error(err_msg)
#             raise InternalErrorException(err_msg)
        
#         return facegallery















#     # def insert_face(self,payload:EnrollFace,file:str) :
#     #     # is_facegalliries_exist = self.face_repo.is_facegalleries_used(payload.facegallery_id)
#     #     payload.image = file
#     #     try:
#     #         facegallery = self.client.create_facegallery(payload)
#     #     except Exception as err:
#     #         err_msg = str(err)
#     #         logger.error(err_msg)
#     #         raise InternalErrorException(err_msg)
        
#     #     return facegallery
    
#     # def encode_image(path_image:str):
#     #     with open(path_image, "rb") as f:
#     #         encoded_string = base64.b64encode(f.read())

#     #     return encoded_string