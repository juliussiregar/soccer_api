# repositories/daily_salary.py

from typing import List, Optional
import uuid
from sqlalchemy.orm import Query
from app.core.database import get_session
from app.models.daily_salary import DailySalary
from app.schemas.daily_salary import CreateNewDailySalary, UpdateDailySalary, DailySalaryFilter
from sqlalchemy.orm import joinedload
from datetime import datetime, timezone

class DailySalaryRepository:
    
    def get_daily_salary_by_id(self, daily_salary_id: int) -> Optional[DailySalary]:
        with get_session() as db:
            daily_salary = (
                db.query(DailySalary)
                .options(joinedload(DailySalary.employee))  # Include employee data
                .filter(DailySalary.id == daily_salary_id)
                .first()
            )
        return daily_salary

    def filtered(self, query: Query, filter: DailySalaryFilter) -> Query:
        if filter.company_id:
            query = query.filter(DailySalary.company_id == filter.company_id)
        return query

    def get_all_filtered(self, filter: DailySalaryFilter) -> List[DailySalary]:
        with get_session() as db:
            query = db.query(DailySalary).options(
                joinedload(DailySalary.company),
                joinedload(DailySalary.employee),  # Include employee data
            )
            query = self.filtered(query, filter).order_by(DailySalary.created_at.desc())
            if filter.limit:
                query = query.limit(filter.limit)
            if filter.page and filter.limit:
                offset = (filter.page - 1) * filter.limit
                query = query.offset(offset)
            return query.all()
        
    def count_by_filter(self, filter: DailySalaryFilter) -> int:
        with get_session() as db:
            query = db.query(DailySalary)
            query = self.filtered(query, filter)
            return query.count()

    def insert(self, payload: CreateNewDailySalary) -> DailySalary:
        daily_salary = DailySalary(
            company_id=payload.company_id,
            employee_id=payload.employee_id,
            hours_rate=payload.hours_rate,
            standard_hours=payload.standard_hours,
            max_late=payload.max_late,
            late_deduction_rate=payload.late_deduction_rate,
            min_overtime=payload.min_overtime,
            overtime_rate=payload.overtime_rate
        )
        with get_session() as db:
            db.add(daily_salary)
            db.flush()
            db.commit()
            db.refresh(daily_salary)
        return daily_salary

    def update(self, daily_salary_id: int, payload: UpdateDailySalary) -> Optional[DailySalary]:
        with get_session() as db:
            daily_salary = db.query(DailySalary).filter(DailySalary.id == daily_salary_id).first()
            if not daily_salary:
                return None
            for key, value in payload.dict(exclude_unset=True).items():
                setattr(daily_salary, key, value)
            daily_salary.updated_at = datetime.now(timezone.utc)
            db.commit()
            db.refresh(daily_salary)
        return daily_salary

    def delete_daily_salary_by_id(self, daily_salary_id: int) -> Optional[DailySalary]:
        with get_session() as db:
            daily_salary = db.query(DailySalary).filter(DailySalary.id == daily_salary_id).first()
            if daily_salary:
                db.delete(daily_salary)
                db.commit()
            return daily_salary
        
    # Ambil Daily Salary berdasarkan employee_id
    def get_by_employee_id(self, employee_id: uuid.UUID) -> Optional[DailySalary]:
        with get_session() as db:
            return db.query(DailySalary).filter(DailySalary.employee_id == employee_id).first()