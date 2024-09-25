from typing import List, Optional, Tuple
import uuid
from passlib.context import CryptContext
from sqlalchemy.orm import Query, joinedload
from sqlalchemy import insert

from app.core.database import get_session
from app.utils.date import get_now
from app.utils.etc import id_generator

from app.utils.exception import UnprocessableException
from app.schemas.visitor import CreateNewVisitor, VisitorFilter
from app.models.visitor import Visitor
from app.models.face import Faces
from app.repositories.client import ClientRepository
from app.repositories.transaction import TransactionRepository
from app.clients.face_api import FaceApiClient
from app.schemas.faceapi_mgt import CreateEnrollFace

client_repo = ClientRepository()
face_api_client = FaceApiClient()
trx_repo = TransactionRepository()

class VisitorRepository :
    def get_visitor(self,username:str,nik:str)->List[Visitor]:
        with get_session() as db:
            visitor = (
                db.query(Visitor)
                .filter(Visitor.username == username, Visitor.nik == nik)
                .first()
                )

        return visitor
    
    def get_visitor_bynik(self,nik:str):
        with get_session() as db:
            visitor = (
                db.query(Visitor)
                .filter(Visitor.nik == nik)
                .first()
                )

        return visitor

    def get_visitorid(self,username:str,nik:str):
        with get_session() as db:
            visitor = (
                db.query(Visitor)
                .filter(Visitor.username == username, Visitor.nik == nik)
                .first()
                )

        return visitor.id
    
    def filtered(self, query: Query, filter: VisitorFilter) -> Query:
        if filter.search is not None:
            query = query.filter(Visitor.username == filter.search)
            # TODO: Add other columns to search

        return query
    
    def get_all_filtered(self, filter: VisitorFilter) -> List[Visitor]:
        with get_session() as db:
            query = db.query(Visitor)

            query = self.filtered(query, filter).order_by(Visitor.created_at.desc())

            if filter.limit is not None:
                query = query.limit(filter.limit)

            if filter.page is not None and filter.limit is not None:
                offset = (filter.page - 1) * filter.limit
                query = query.offset(offset)

            return query.options(joinedload(Visitor.face), joinedload(Visitor.client)).all()
    def count_by_filter(self, filter: VisitorFilter) -> int:
        with get_session() as db:
            query = db.query(Visitor)

            query = self.filtered(query, filter)

            return query.count()

                
    def insert(self, payload: CreateNewVisitor) -> Visitor:
        check_client = client_repo.is_facegalleries_used(payload.client_name)
        if not check_client:
            client = client_repo.insert_client(client_name=payload.client_name)
            client_id = client_repo.get_client_id(client_name= client.client_name)

        else:
            client_id = client_repo.get_client_id(client_name= payload.client_name)
            client = client_repo.get_client_by_id(client_id=client_id)

        visitor = Visitor()
        visitor.username = payload.username
        visitor.full_name =payload.full_name
        visitor.nik = payload.nik
        visitor.born_date = payload.born_date
        visitor.company = payload.company_name
        visitor.address = payload.address
        visitor.email = payload.email
        visitor.client_id = client_id
        visitor.created_at = get_now()

        with get_session() as db:
            db.add(visitor)
            db.flush()
            db.commit()
            db.refresh(visitor)

        face = self.face_insert(payload.image,visitor.id,client_id)

        return visitor,client,face

    def face_insert(self,image:str,visitor_id:uuid,client_id:uuid) -> Faces:
        face = Faces()
        face.image_base64 = image
        face.visitor_id = visitor_id
        face.client_id = client_id
        face.created_at = get_now()
        with get_session() as db:
            db.add(face)
            db.flush()
            db.commit()
            db.refresh(face)

        return face 
    
    def is_username_used(self, username: str, except_id: Optional[str] = None) -> bool:
        with get_session() as db:
            client_count = (
                db.query(Visitor)
                .filter(Visitor.username == username, Visitor.id != except_id)
                .count()
            )

        return client_count > 0
    
    def is_nik_used(self, nik: str, except_id: Optional[str] = None) -> bool:
        with get_session() as db:
            client_count = (
                db.query(Visitor)
                .filter(Visitor.nik == nik, Visitor.id != except_id)
                .count()
            )

        return client_count > 0
