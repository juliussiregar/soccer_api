# repositories/employee.py

from typing import List, Optional
import uuid
from sqlalchemy.orm import Query
from app.core.database import get_session
from app.models.employee import Employee
from app.schemas.employee import CreateNewEmployee, UpdateEmployee, EmployeeFilter
from sqlalchemy.orm import joinedload
from datetime import datetime, timezone

class EmployeeRepository:
    
    def get_employee_by_id(self, employee_id: uuid.UUID) -> Optional[Employee]:
        with get_session() as db:
            employee = db.query(Employee).filter(Employee.id == employee_id).first()
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
            return query.all()

    def count_by_filter(self, filter: EmployeeFilter) -> int:
        with get_session() as db:
            query = db.query(Employee)
            query = self.filtered(query, filter)
            return query.count()

    def insert(self, payload: CreateNewEmployee) -> Employee:
        employee = Employee(
            company_id=payload.company_id,
            position_id=payload.position_id,
            user_name=payload.user_name,
            nik=payload.nik,
            email=payload.email
        )
        with get_session() as db:
            db.add(employee)
            db.flush()
            db.commit()
            db.refresh(employee)
        return employee

    def update(self, employee_id: uuid.UUID, payload: UpdateEmployee) -> Optional[Employee]:
        with get_session() as db:
            employee = db.query(Employee).filter(Employee.id == employee_id).first()
            if not employee:
                return None
            if payload.user_name:
                employee.user_name = payload.user_name
            if payload.nik:
                employee.nik = payload.nik
            if payload.email:
                employee.email = payload.email
            employee.updated_at = datetime.now(timezone.utc)
            db.commit()
            db.refresh(employee)
        return employee

    def delete_employee_by_id(self, employee_id: uuid.UUID) -> Optional[Employee]:
        with get_session() as db:
            employee = db.query(Employee).filter(Employee.id == employee_id).first()
            if employee:
                db.delete(employee)
                db.commit()
            return employee
        
    def get_employees_by_company_id(self, company_id: uuid.UUID) -> List[Employee]:
        with get_session() as db:
            employees = db.query(Employee).filter(Employee.company_id == company_id).all()
        return employees
