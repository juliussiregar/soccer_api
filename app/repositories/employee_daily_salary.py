# repositories/employee_daily_salary.py

from typing import List, Optional
import uuid
from sqlalchemy.orm import Query
from app.core.database import get_session
from app.models.employee import Employee
from app.models.employee_daily_salary import EmployeeDailySalary
from app.schemas.employee_daily_salary import CreateNewEmployeeDailySalary, UpdateEmployeeDailySalary, EmployeeDailySalaryFilter
from sqlalchemy.orm import joinedload
from datetime import datetime, timezone, date


class EmployeeDailySalaryRepository:

    def get_employee_daily_salary_by_id(self, employee_daily_salary_id: int) -> Optional[EmployeeDailySalary]:
        with get_session() as db:
            employee_daily_salary = db.query(EmployeeDailySalary).filter(EmployeeDailySalary.id == employee_daily_salary_id).first()
        return employee_daily_salary

    def filtered(self, query: Query, filter: EmployeeDailySalaryFilter) -> Query:
        query = query.join(Employee, EmployeeDailySalary.employee_id == Employee.id)

        if filter.search:
            query = query.filter(Employee.user_name.ilike(f"%{filter.search}%"))
        if filter.employee_id:
            query = query.filter(EmployeeDailySalary.employee_id == filter.employee_id)
        if filter.company_id:
            query = query.filter(Employee.company_id == filter.company_id)
        return query

    def get_all_filtered(self, filter: EmployeeDailySalaryFilter) -> List[EmployeeDailySalary]:
        with get_session() as db:
            query = db.query(EmployeeDailySalary).options(joinedload(EmployeeDailySalary.employee))
            query = self.filtered(query, filter).order_by(EmployeeDailySalary.created_at.desc())
            if filter.limit:
                query = query.limit(filter.limit)
            if filter.page and filter.limit:
                offset = (filter.page - 1) * filter.limit
                query = query.offset(offset)
            return query.all()

    def count_by_filter(self, filter: EmployeeDailySalaryFilter) -> int:
        with get_session() as db:
            query = db.query(EmployeeDailySalary)
            query = self.filtered(query, filter)
            return query.count()

    def insert(self, payload: CreateNewEmployeeDailySalary) -> EmployeeDailySalary:
        employee_daily_salary = EmployeeDailySalary(
            employee_id=payload.employee_id,
            work_date=payload.work_date,
            hours_worked=payload.hours_worked,
            late_deduction=payload.late_deduction,
            month=payload.month,
            year=payload.year,
            normal_salary=payload.normal_salary,
            total_salary=payload.total_salary
        )
        with get_session() as db:
            db.add(employee_daily_salary)
            db.flush()
            db.commit()
            db.refresh(employee_daily_salary)
        return employee_daily_salary

    def update(self, employee_daily_salary_id: int, payload: UpdateEmployeeDailySalary) -> Optional[EmployeeDailySalary]:
        with get_session() as db:
            employee_daily_salary = db.query(EmployeeDailySalary).filter(EmployeeDailySalary.id == employee_daily_salary_id).first()
            if not employee_daily_salary:
                return None
            for key, value in payload.dict(exclude_unset=True).items():
                setattr(employee_daily_salary, key, value)
            employee_daily_salary.updated_at = datetime.now(timezone.utc)
            db.commit()
            db.refresh(employee_daily_salary)
        return employee_daily_salary

    def delete_employee_daily_salary_by_id(self, employee_daily_salary_id: int) -> Optional[EmployeeDailySalary]:
        with get_session() as db:
            employee_daily_salary = db.query(EmployeeDailySalary).filter(EmployeeDailySalary.id == employee_daily_salary_id).first()
            if employee_daily_salary:
                db.delete(employee_daily_salary)
                db.commit()
            return employee_daily_salary

    def delete_employee_daily_salary_by_employee_id(self, employee_id: uuid.UUID) -> Optional[EmployeeDailySalary]:
        with get_session() as db:
            employee_daily_salary = db.query(EmployeeDailySalary).filter(EmployeeDailySalary.employee_id == employee_id).delete()
            db.commit()

        return employee_daily_salary

    # Ambil Employee Daily Salary berdasarkan employee_id
    def get_by_employee_id(self, employee_id: uuid.UUID) -> Optional[EmployeeDailySalary]:
        with get_session() as db:
            return db.query(EmployeeDailySalary).filter(EmployeeDailySalary.employee_id == employee_id).first()

    def get_by_employee_id_and_date(self, employee_id: uuid.UUID, work_date: date):
        with get_session() as db:
            return (
            db.query(EmployeeDailySalary)
            .filter(EmployeeDailySalary.employee_id == employee_id)
            .filter(EmployeeDailySalary.work_date == work_date)
            .first()
        )

    def get_all_by_month_year(self, employee_id: uuid.UUID, month: int, year: int):
        with get_session() as db:
            return (
                db.query(EmployeeDailySalary)
                .filter(EmployeeDailySalary.employee_id == employee_id)
                .filter(EmployeeDailySalary.month == month)
                .filter(EmployeeDailySalary.year == year)
                .first()
            )