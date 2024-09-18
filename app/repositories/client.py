from typing import List, Optional, Tuple
import uuid
from passlib.context import CryptContext
from sqlalchemy.orm import Query, joinedload
from sqlalchemy import insert

from app.core.database import get_session
from app.utils.date import get_now
from app.utils.etc import id_generator

from app.utils.exception import UnprocessableException
from app.schemas.faceapi_mgt import CreateFaceGallery
from app.models.client import Client

class ClientRepository :
    def insert(self, client_name:str) -> Client:
        client = Client()
        client.client_name = client_name
        client.created_at = get_now()
        with get_session() as db:
            db.add(client)
            db.flush()
            db.commit()
            db.refresh(client)

        return client

    def insert_client(self,client_name:str) -> Client:
        client = Client()
        client.client_name = client_name
        client.created_at = get_now()
        with get_session() as db:
            db.add(client)
            db.flush()
            db.commit()
            db.refresh(client)

        return client
    
    def get_client_id(self,client_name:str):
        with get_session() as db:
            client = (
                db.query(Client)
                .filter(Client.client_name == client_name)
                .first()
            )

        return client
    
    def get_client_by_id(self,client_id:uuid.UUID):
        with get_session() as db:
            client = (
                db.query(Client)
                .filter(Client.id == client_id)
                .first()
            )

        return client
    
    def is_facegalleries_used(self, client_name: str, except_id: Optional[str] = None) -> bool:
        with get_session() as db:
            client_count = (
                db.query(Client)
                .filter(Client.client_name == client_name, Client.id != except_id)
                .count()
            )

        return client_count > 0
