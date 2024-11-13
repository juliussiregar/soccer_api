# repositories/employee.py

from typing import List, Optional
import uuid
from sqlalchemy.orm import Query, joinedload
from app.core.database import get_session
from app.utils.date import get_now
from app.models.employee import Employee
from app.schemas.employee import CreateNewEmployee, EmployeeFilter

class EmployeeRepository:
    
    # Metode baru untuk mendapatkan semua Employee berdasarkan company_id
    def get_employees_by_company_id(self, company_id: uuid.UUID) -> List[Employee]:
        """
        Mengambil daftar Employee berdasarkan company_id.

        Args:
            company_id (uuid.UUID): ID perusahaan.

        Returns:
            List[Employee]: Daftar Employee yang berafiliasi dengan company_id tertentu.
        """
        with get_session() as db:
            employees = (
                db.query(Employee)
                .filter(Employee.company_id == company_id)
                .options(
                    joinedload(Employee.company),
                    joinedload(Employee.attendance),
                    joinedload(Employee.daily_salary),
                    joinedload(Employee.employee_daily_salary),
                    joinedload(Employee.employee_monthly_salary)
                )
                .all()
            )
        return employees

    # Metode lain yang sudah ada
    def get_employee(self, user_name: str, nik: str) -> Optional[Employee]:
        with get_session() as db:
            employee = (
                db.query(Employee)
                .filter(Employee.user_name == user_name, Employee.nik == nik)
                .first()
            )
        return employee
    
    def get_employee_by_nik(self, nik: str) -> Optional[Employee]:
        with get_session() as db:
            employee = (
                db.query(Employee)
                .filter(Employee.nik == nik)
                .first()
            )
        return employee

    def get_employee_by_id(self, id: uuid.UUID) -> Optional[Employee]:
        with get_session() as db:
            employee = (
                db.query(Employee)
                .filter(Employee.id == id)
                .first()
            )
        return employee

    def filtered(self, query: Query, filter: EmployeeFilter) -> Query:
        if filter.search:
            query = query.filter(Employee.user_name.contains(filter.search))
        return query

    def get_all_filtered(self, filter: EmployeeFilter) -> List[Employee]:
        with get_session() as db:
            query = db.query(Employee)
            query = self.filtered(query, filter).order_by(Employee.created_at.desc())

            if filter.limit:
                query = query.limit(filter.limit)

            if filter.page and filter.limit:
                offset = (filter.page - 1) * filter.limit
                query = query.offset(offset)

            return query.options(
                joinedload(Employee.company),
                joinedload(Employee.attendance),
                joinedload(Employee.daily_salary),
                joinedload(Employee.employee_daily_salary),
                joinedload(Employee.employee_monthly_salary)
            ).all()

    def count_by_filter(self, filter: EmployeeFilter) -> int:
        with get_session() as db:
            query = db.query(Employee)
            query = self.filtered(query, filter)
            return query.count()

    def insert(self, payload: CreateNewEmployee) -> Employee:
        employee = Employee()
        employee.user_name = payload.user_name
        employee.nik = payload.nik
        employee.email = payload.email
        employee.position = payload.position
        employee.created_at = get_now()

        with get_session() as db:
            db.add(employee)
            db.flush()
            db.commit()
            db.refresh(employee)

        return employee

    def is_username_used(self, user_name: str, except_id: Optional[uuid.UUID] = None) -> bool:
        with get_session() as db:
            employee_count = (
                db.query(Employee)
                .filter(Employee.user_name == user_name, Employee.id != except_id)
                .count()
            )
        return employee_count > 0

    def is_nik_used(self, nik: str, except_id: Optional[uuid.UUID] = None) -> bool:
        with get_session() as db:
            employee_count = (
                db.query(Employee)
                .filter(Employee.nik == nik, Employee.id != except_id)
                .count()
            )
        return employee_count > 0

    def delete_employee_by_id(self, id: uuid.UUID) -> Optional[Employee]:
        with get_session() as db:
            employee = db.query(Employee).filter(Employee.id == id).first()
            if employee:
                db.delete(employee)
                db.commit()
            return employee

    def get_all_employees(self) -> List[Employee]:
        with get_session() as db:
            employees = db.query(Employee).all()
        return employees
