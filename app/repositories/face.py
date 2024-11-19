from typing import List, Optional
import uuid

from sqlalchemy import func
from sqlalchemy.orm import joinedload

from app.core.database import get_session
from app.models.company import Company
from app.models.employee import Employee
from app.models.face import Face
from app.schemas.face_mgt import CreateFace, UpdateFace


class FaceRepository:

    def get_by_id(self, face_id: uuid.UUID) -> Optional[Face]:
        """Dapatkan data Face berdasarkan ID"""
        with get_session() as db:
            return db.query(Face).filter(Face.id == face_id).first()

    def get_all_faces(self, company_id: Optional[uuid.UUID], limit: int, offset: int) -> List[Face]:
        """
        Retrieve paginated faces, optionally filtered by company_id.
        """
        with get_session() as db:
            query = db.query(Face).options(joinedload(Face.company), joinedload(Face.employee))

            if company_id:
                query = query.filter(Face.company_id == company_id)

            query = query.limit(limit).offset(offset)
            return query.all()

    def count_faces(self, company_id: Optional[uuid.UUID] = None) -> int:
        """
        Count total number of faces, optionally filtered by company_id.
        """
        with get_session() as db:
            query = db.query(Face)

            if company_id:
                query = query.filter(Face.company_id == company_id)

            return query.count()

    def get_by_id(self, face_id: uuid.UUID) -> Optional[Face]:
        """
        Retrieve a face by its ID.
        """
        with get_session() as db:
            return db.query(Face).filter(Face.id == face_id).first()

    def create_face(self, payload: CreateFace) -> Face:
        """Tambah data Face baru ke database"""
        face = Face(
            company_id=payload.company_id,
            employee_id=payload.employee_id,
            photo=payload.photo
        )
        with get_session() as db:
            db.add(face)
            db.flush()
            db.commit()
            db.refresh(face)
        return face

    def update_face(self, face_id: uuid.UUID, payload: UpdateFace) -> Optional[Face]:
        """Perbarui data Face berdasarkan ID"""
        with get_session() as db:
            face = db.query(Face).filter(Face.id == face_id).first()
            if not face:
                return None

            # Update company_id if provided in the payload
            if payload.company_id is not None:
                face.company_id = payload.company_id

            # Update employee_id if provided in the payload
            if payload.employee_id is not None:
                face.employee_id = payload.employee_id

            # Update photo if provided in the payload
            if payload.photo is not None:
                face.photo = payload.photo

            # Update the updated_at timestamp
            face.updated_at = func.now()

            # Commit the changes to the database
            db.commit()
            db.refresh(face)

        return face

    def delete_face(self, face_id: uuid.UUID) -> Optional[Face]:
        """Soft delete data Face berdasarkan ID"""
        with get_session() as db:
            face = db.query(Face).filter(Face.id == face_id).first()
            if face:
                db.delete(face)
                db.commit()
            return face

    def get_face_byvisitorid(self, employee_id: str) -> Face:
        with get_session() as db:
            face = (
                db.query(Face)
                .filter(Face.employee_id == employee_id)
                .first()
            )

        return face

    def get_all_faces_with_employees(self):
        with get_session() as db:
            results = (
                db.query(
                    Face.id,
                    Face.employee_id,
                    Face.company_id,
                    Employee.nik,
                    Employee.user_name,
                    Face.photo,
                    Face.created_at,
                    Company.name.label("company_name")  # Fetch company name explicitly
                )
                .join(Employee, Face.employee_id == Employee.id, isouter=True)  # LEFT JOIN with Employee
                .join(Company, Face.company_id == Company.id, isouter=True)  # LEFT JOIN with Company
                .all()
            )
        return results

    def get_visitorid_by_imagebase64(self, image: str) -> Face:
        with get_session() as db:
            face = (
                db.query(Face)
                .filter(Face.photo == image)
                .first()
            )

        return face.visitor_id

    def delete_face_byuser_id(self, employee_id=uuid) -> Face:
        with get_session() as db:
            face = (
                db.query(Face)
                .filter(Face.employee_id == employee_id)
                .delete()
            )
            db.commit()

        return face
