from typing import List, Optional
import uuid
from sqlalchemy.orm import Query

from app.core.database import get_session
from app.models.company import Company
from app.schemas.company import CreateNewCompany, UpdateCompany, CompanyFilter
from sqlalchemy.orm import joinedload
from app.utils.date import get_now


class CompanyRepository:

    def get_company_by_id(self, company_id: uuid.UUID) -> Optional[Company]:
        with get_session() as db:
            company = db.query(Company).filter(
                Company.id == company_id,
                Company.deleted_at.is_(None)  # Include only companies with deleted_at as None
            ).first()
        return company

    def filtered(self, query: Query, filter: CompanyFilter) -> Query:
        if filter.search:
            query = query.filter(Company.name.contains(filter.search))
        return query

    def get_all_filtered(self, filter: CompanyFilter) -> List[Company]:
        with get_session() as db:
            query = db.query(Company).options(joinedload(Company.position))
            # Filter based on the provided filters
            query = self.filtered(query, filter)

            # Include users with null deleted_at
            query = query.filter(Company.deleted_at.is_(None))

            query = query.order_by(Company.created_at.desc())

            if filter.limit:
                query = query.limit(filter.limit)

            if filter.page and filter.limit:
                offset = (filter.page - 1) * filter.limit
                query = query.offset(offset)

            return query.all()

    def count_by_filter(self, filter: CompanyFilter) -> int:
        with get_session() as db:
            query = db.query(Company)
            # Filter based on the provided filters
            query = self.filtered(query, filter)

            # Include users with null deleted_at
            query = query.filter(Company.deleted_at.is_(None))

            return query.count()

    def insert(self, payload: CreateNewCompany) -> Company:
        company = Company(
            name=payload.name,
            logo=payload.logo,
            start_time=payload.start_time,
            end_time=payload.end_time,
        )

        with get_session() as db:
            db.add(company)
            db.flush()
            db.commit()
            db.refresh(company)

        return company

    def update(self, company_id: uuid.UUID, payload: UpdateCompany) -> Optional[Company]:
        with get_session() as db:
            company = db.query(Company).filter(Company.id == company_id).first()

            if not company:
                return None

            if payload.name is not None:
                company.name = payload.name
            if payload.logo is not None:
                company.logo = payload.logo
            if payload.start_time is not None:
                company.start_time = payload.start_time
            if payload.end_time is not None:
                company.end_time = payload.end_time

            company.updated_at = get_now()
            db.commit()
            db.refresh(company)

        return company

    def delete_company_by_id(self, company_id: uuid.UUID) -> Optional[Company]:
        with get_session() as db:
            company = db.query(Company).filter(Company.id == company_id).first()
            if not company:
                return False

            # Soft delete - update deleted_at timestamp
            company.deleted_at = get_now()

            db.commit()
            return company
