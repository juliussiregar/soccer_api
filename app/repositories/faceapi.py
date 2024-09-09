# from typing import List, Tuple
# from passlib.context import CryptContext
# from sqlalchemy.orm import Query, joinedload
# from sqlalchemy import insert

# from app.core.database import get_session
# from app.models.face import FaceGalleries
# from app.utils.date import get_now
# from app.utils.etc import id_generator

# from app.utils.exception import UnprocessableException
# from app.schemas.faceapi_mgt import CreateFaceGallery

# class FaceApiRepository :
#     def insert(self, payload: CreateFaceGallery) -> FaceGalleries:
#         pass
    
#     def is_facegalleries_used(self, facegallery_id: str, except_id: int = 0) -> bool:
#         with get_session() as db:
#             facegallery_count = (
#                 db.query(FaceGalleries)
#                 .filter(FaceGalleries.facegallery_id == facegallery_id, FaceGalleries.id != except_id)
#                 .count()
#             )

#         return facegallery_count > 0
