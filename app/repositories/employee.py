# repositories/employee.py

from typing import List, Optional, Tuple
import uuid
from sqlalchemy.orm import Query
from app.core.database import get_session
from app.models.employee import Employee
from app.models.face import Face
from app.schemas.employee import CreateNewEmployee, UpdateEmployee, EmployeeFilter
from sqlalchemy.orm import joinedload
from datetime import datetime, timezone

class EmployeeRepository:
    
    def get_employee_by_id(self, employee_id: uuid.UUID) -> Optional[Employee]:
        with get_session() as db:
            employee = db.query(Employee).filter(Employee.id == employee_id).options(joinedload(Employee.face)).first()
        return employee

    def filtered(self, query: Query, filter: EmployeeFilter) -> Query:
        if filter.search:
            query = query.filter(Employee.user_name.contains(filter.search))
        if filter.company_id:
            query = query.filter(Employee.company_id == filter.company_id)
        return query

    def get_all_filtered(self, filter: EmployeeFilter) -> List[Employee]:
        with get_session() as db:
            query = db.query(Employee).options(joinedload(Employee.company))
            query = self.filtered(query, filter).order_by(Employee.created_at.desc())
            if filter.limit:
                query = query.limit(filter.limit)
            if filter.page and filter.limit:
                offset = (filter.page - 1) * filter.limit
                query = query.offset(offset)
            return query.options(joinedload(Employee.face), joinedload(Employee.company)).all()

    def count_by_filter(self, filter: EmployeeFilter) -> int:
        with get_session() as db:
            query = db.query(Employee)
            query = self.filtered(query, filter)
            return query.count()

    def insert(self, payload: CreateNewEmployee) -> Tuple[Employee, Optional[Face]]:
        employee = Employee(
            company_id=payload.company_id,  # Perbaikan: Hapus koma
            position_id=payload.position_id,
            user_name=payload.user_name,
            nik=payload.nik,
            email=payload.email,
        )

        with get_session() as db:
            db.add(employee)
            db.flush()  # Mendapatkan `employee.id` sebelum membuat Face

            face = None
            if payload.photo:
                face = Face(
                    company_id=employee.company_id,
                    employee_id=employee.id,
                    photo=payload.photo
                )
                db.add(face)

            db.commit()
            db.refresh(employee)
            if face:
                db.refresh(face)

        return employee, face

    def face_insert(self, company_id: uuid, employee_id: uuid, photo: str) -> Face:
        face = Face()
        face.company_id = company_id
        face.employee_id = employee_id
        if not photo:
            raise ValueError("Photo is required to create a face record.")

        face.photo = photo

        with get_session() as db:
            db.add(face)
            db.flush()
            db.commit()
            db.refresh(face)

        return face

    def update(self, employee_id: uuid.UUID, payload: UpdateEmployee) -> Optional[Employee]:
        with get_session() as db:
            employee = db.query(Employee).filter(Employee.id == employee_id).first()
            if not employee:
                raise ValueError(f"Employee with ID '{employee_id}' not found.")

            # Validasi unik NIK dan email
            if payload.nik and self.is_nik_used(payload.nik, except_id=str(employee_id)):
                raise ValueError(f"NIK '{payload.nik}' is already in use.")
            if payload.email:
                email_exists = db.query(Employee).filter(
                    Employee.email == payload.email,
                    Employee.id != employee_id
                ).first()
                if email_exists:
                    raise ValueError(f"Email '{payload.email}' is already in use.")

            # Perbarui atribut Employee
            if payload.user_name is not None:
                employee.user_name = payload.user_name
            if payload.nik is not None:
                employee.nik = payload.nik
            if payload.email is not None:
                employee.email = payload.email

            # Perbarui entitas Face jika photo diberikan
            if payload.photo:
                face = db.query(Face).filter(Face.employee_id == employee_id).first()
                if face:
                    face.photo = payload.photo
                else:
                    face = Face(
                        company_id=employee.company_id,
                        employee_id=employee_id,
                        photo=payload.photo
                    )
                    db.add(face)

            employee.updated_at = datetime.now(timezone.utc)
            db.commit()
            db.refresh(employee)

        return employee

    def delete_employee_by_id(self, employee_id: uuid.UUID) -> Optional[Employee]:
        with get_session() as db:
            employee = db.query(Employee).filter(Employee.id == employee_id).first()
            if not employee:
                raise ValueError(f"Employee with ID '{employee_id}' not found.")

            # Hapus entitas Face terkait
            face = db.query(Face).filter(Face.employee_id == employee_id).first()
            if face:
                db.delete(face)

            db.delete(employee)
            db.commit()

        return employee

    def get_employees_by_company_id(self, company_id: uuid.UUID) -> List[Employee]:
        with get_session() as db:
            employees = db.query(Employee).filter(Employee.company_id == company_id).all()
        return employees

    def is_nik_used(self, nik: str, except_id: Optional[str] = None) -> bool:
        with get_session() as db:
            employee_count = (
                db.query(Employee)
                .filter(Employee.nik == nik, Employee.id != except_id)
                .count()
            )

        return employee_count > 0

    def get_employee_bynik(self,nik:str):
        with get_session() as db:
            employee = (
                db.query(Employee)
                .filter(Employee.nik == nik)
                .first()
                )

        return employee

    def is_email_used(self, email: str, except_id: Optional[str] = None) -> bool:
        with get_session() as db:
            employee = (
                db.query(Employee)
                .filter(Employee.email == email)
                .filter(Employee.id != except_id)
                .first()
            )
        return employee is not None

    def is_user_name_used(self, user_name: str, except_id: Optional[str] = None) -> bool:
        with get_session() as db:
            employee_count = (
                db.query(Employee)
                .filter(Employee.user_name == user_name)
                .filter(Employee.id != except_id)
                .count()
            )

        return employee_count > 0