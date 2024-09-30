from typing import List, Optional, Tuple
import uuid
from passlib.context import CryptContext
from sqlalchemy.orm import Query, joinedload
from sqlalchemy import insert

from app.core.database import get_session
from app.utils.date import get_now
from app.utils.etc import id_generator

from app.utils.exception import UnprocessableException
from app.models.face import Faces


class FaceRepository :
    def get_face_byvisitorid(self,visitor_id:str)->Faces:
        with get_session() as db:
            face = (
                db.query(Faces)
                .filter(Faces.visitor_id == visitor_id)
                .first()
                )

        return face
    
    def get_visitorid_by_imagebase64(self,image:str)->Faces:
        with get_session() as db:
            face = (
                db.query(Faces)
                .filter(Faces.image_base64 == image)
                .first()
                )

        return face.visitor_id
    
    def delete_face_byuser_id(self,visitor_id=uuid)->Faces:
        with get_session() as db:
            face = (
                db.query(Faces)
                .filter(Faces.visitor_id == visitor_id)
                .delete()
                )
            db.commit()

        return face
        
