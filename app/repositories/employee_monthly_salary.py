# repositories/employee_monthly_salary.py

from typing import List, Optional
import uuid

from sqlalchemy import func, or_
from sqlalchemy.orm import Query
from app.core.database import get_session
from app.models.employee_daily_salary import EmployeeDailySalary
from app.models.employee_monthly_salary import EmployeeMonthlySalary
from app.schemas.employee_monthly_salary import CreateNewEmployeeMonthlySalary, UpdateEmployeeMonthlySalary, EmployeeMonthlySalaryFilter
from sqlalchemy.orm import joinedload
from datetime import datetime, timezone, date


class EmployeeMonthlySalaryRepository:

    def get_employee_monthly_salary_by_id(self, employee_monthly_salary_id: int) -> Optional[EmployeeMonthlySalary]:
        with get_session() as db:
            employee_monthly_salary = db.query(EmployeeMonthlySalary).filter(EmployeeMonthlySalary.id == employee_monthly_salary_id).first()
        return employee_monthly_salary

    def filtered(self, query: Query, filter: EmployeeMonthlySalaryFilter) -> Query:
        if filter.employee_id:
            query = query.filter(EmployeeMonthlySalary.employee_id == filter.employee_id)
        return query

    def get_all_filtered(self, filter: EmployeeMonthlySalaryFilter) -> List[EmployeeMonthlySalary]:
        with get_session() as db:
            query = db.query(EmployeeMonthlySalary).options(joinedload(EmployeeMonthlySalary.employee))
            query = self.filtered(query, filter).order_by(EmployeeMonthlySalary.created_at.desc())
            if filter.limit:
                query = query.limit(filter.limit)
            if filter.page and filter.limit:
                offset = (filter.page - 1) * filter.limit
                query = query.offset(offset)
            return query.all()

    def count_by_filter(self, filter: EmployeeMonthlySalaryFilter) -> int:
        with get_session() as db:
            query = db.query(EmployeeMonthlySalary)
            query = self.filtered(query, filter)
            return query.count()

    def insert(self, payload: CreateNewEmployeeMonthlySalary) -> EmployeeMonthlySalary:
        employee_monthly_salary = EmployeeMonthlySalary(
            employee_id=payload.employee_id,
            month=payload.month,
            year=payload.year,
            normal_salary=payload.normal_salary,
            total_salary=payload.total_salary
        )
        with get_session() as db:
            db.add(employee_monthly_salary)
            db.flush()
            db.commit()
            db.refresh(employee_monthly_salary)
        return employee_monthly_salary

    def update(self, employee_monthly_salary_id: int, payload: UpdateEmployeeMonthlySalary) -> Optional[EmployeeMonthlySalary]:
        with get_session() as db:
            employee_monthly_salary = db.query(EmployeeMonthlySalary).filter(EmployeeMonthlySalary.id == employee_monthly_salary_id).first()
            if not employee_monthly_salary:
                return None
            for key, value in payload.dict(exclude_unset=True).items():
                setattr(employee_monthly_salary, key, value)
            employee_monthly_salary.updated_at = datetime.now(timezone.utc)
            db.commit()
            db.refresh(employee_monthly_salary)
        return employee_monthly_salary

    def delete_employee_monthly_salary_by_id(self, employee_monthly_salary_id: int) -> Optional[EmployeeMonthlySalary]:
        with get_session() as db:
            employee_monthly_salary = db.query(EmployeeMonthlySalary).filter(EmployeeMonthlySalary.id == employee_monthly_salary_id).first()
            if employee_monthly_salary:
                db.delete(employee_monthly_salary)
                db.commit()
            return employee_monthly_salary

    def delete_employee_monthly_salary_by_employee_id(self, employee_id: uuid.UUID) -> Optional[EmployeeMonthlySalary]:
        with get_session() as db:
            employee_monthly_salary = db.query(EmployeeMonthlySalary).filter(EmployeeMonthlySalary.employee_id == employee_id).delete()
            db.commit()

        return employee_monthly_salary

    # Ambil Employee Daily Salary berdasarkan employee_id
    def get_by_employee_id(self, employee_id: uuid.UUID) -> Optional[EmployeeMonthlySalary]:
        with get_session() as db:
            return db.query(EmployeeMonthlySalary).filter(EmployeeMonthlySalary.employee_id == employee_id).first()

    def get_by_employee_id_and_month(self, employee_id: uuid.UUID, month: int):
        with get_session() as db:
            return (
            db.query(EmployeeMonthlySalary)
            .filter(EmployeeMonthlySalary.employee_id == employee_id)
            .filter(EmployeeMonthlySalary.month == month)
            .first()
        )

    def get_by_employee_id_and_month_year(self, employee_id: uuid.UUID, month: int, year: int):
        with get_session() as db:
            return (
            db.query(EmployeeMonthlySalary)
            .filter(EmployeeMonthlySalary.employee_id == employee_id)
            .filter(EmployeeMonthlySalary.month == month)
            .filter(EmployeeMonthlySalary.year == year)
            .first()
        )

    def get_total_monthly_salary_by_employee(self, month: int, year: int):
        """Mengambil total gaji bulanan per karyawan berdasarkan bulan dan tahun,
        hanya untuk salary bulanan yang belum diupdate (updated_by is None).
        """
        with get_session() as db:
            result = (
                db.query(
                    EmployeeDailySalary.employee_id,
                    func.max(EmployeeDailySalary.normal_salary).label('normal_salary'),
                    func.sum(EmployeeDailySalary.total_salary).label('total_monthly_salary')
                )
                .join(
                    EmployeeMonthlySalary,
                    (EmployeeDailySalary.employee_id == EmployeeMonthlySalary.employee_id) &
                    (EmployeeDailySalary.month == EmployeeMonthlySalary.month) &
                    (EmployeeDailySalary.year == EmployeeMonthlySalary.year),
                    isouter=True
                )
                .filter(
                    EmployeeDailySalary.month == month,
                    EmployeeDailySalary.year == year,
                    or_(EmployeeMonthlySalary.id.is_(None), EmployeeMonthlySalary.updated_by.is_(None))
                )
                .group_by(EmployeeDailySalary.employee_id)
                .all()
            )
        return result

