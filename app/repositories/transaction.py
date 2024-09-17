from typing import List, Optional, Tuple
import uuid
from passlib.context import CryptContext
from sqlalchemy.orm import Query, joinedload
from sqlalchemy import insert

from app.core.database import get_session
from app.utils.date import get_now
from app.utils.etc import id_generator

from app.utils.exception import UnprocessableException
from app.schemas.visitor import CreateNewVisitor
from app.models.visitor import Visitor
from app.models.transaction import Transaction
from app.repositories.client import ClientRepository

client_repo = ClientRepository()

class TransactionRepository :
    def insert_trx(self,visitor_id:uuid,client_id:uuid)->Transaction :
        trx = Transaction()
        trx.client_id = client_id
        trx.visitor_id = visitor_id
        trx.created_at = get_now()

        with get_session() as db:
            db.add(trx)
            db.flush()
            db.commit()
            db.refresh(trx)

        return trx
    
    def insert_transaction(self,trx_id:uuid,visitor_id:uuid,client_id:uuid,url:str)->Transaction :
        trx = Transaction()
        trx.id = trx_id
        trx.client_id = client_id
        trx.visitor_id = visitor_id
        trx.url = url
        trx.created_at = get_now()

        with get_session() as db:
            db.add(trx)
            db.flush()
            db.commit()
            db.refresh(trx)

        return trx
    
    def get_trxid_by_visitor_id(self,visitor_id:uuid)->Transaction:
        with get_session() as db:
            trx = (
                db.query(Transaction)
                .filter(Transaction.visitor_id == visitor_id)
                .first()
            )

        return trx
    
    def get_trxid_by_clientid(self,client_id:uuid)->Transaction:
        with get_session() as db:
            trx = (
                db.query(Transaction)
                .filter(Transaction.client_id == client_id)
                .first()
            )

        return trx
    
    
    def get_all_trxid_by_clientid(self,client_id:uuid)->List[Transaction]:
        with get_session() as db:
            trx = (
                db.query(Transaction)
                .filter(Transaction.client_id == client_id)
                .all()
            )

        return trx
