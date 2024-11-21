from datetime import time
from typing import List, Optional
import uuid
from sqlalchemy.orm import Query

from app.core.database import get_session
from app.models.company import Company
from app.schemas.company import CreateNewCompany, UpdateCompany, CompanyFilter, CreateFaceGalleryCompany
from sqlalchemy.orm import joinedload
from app.utils.date import get_now


class CompanyRepository:

    def get_company(self):
        with get_session() as db:
            client = (
                db.query(Company)
                .first()
            )

        return client

    def get_company_by_id(self, company_id: uuid.UUID) -> Optional[Company]:
        with get_session() as db:
            company = db.query(Company).filter(
                Company.id == company_id,
                Company.deleted_at.is_(None)  # Include only companies with deleted_at as None
            ).first()
        return company

    def get_company_id(self, company_id: uuid.UUID):
        with get_session() as db:
            client = (
                db.query(Company)
                .filter(Company.id == company_id)
                .first()
            )

        return client.id

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

    def insertFaceGallery(self, company_id: uuid.UUID) -> Company:
        company = Company(
            id=company_id,
            name="default_name",
            logo="default_logo",
            start_time=time(0, 0),
            end_time=time(23, 59),
            created_at= get_now()
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

    def get_company_name_by_id(self, company_id: uuid.UUID) -> Optional[str]:
        with get_session() as db:
            company = db.query(Company).filter(Company.id == company_id).first()
            return company.name if company else None

    def is_facegalleries_used(self, company_id: uuid.UUID, except_id: Optional[str] = None) -> bool:
        with get_session() as db:
            client_count = (
                db.query(Company)
                .filter(Company.id == company_id, Company.id != except_id)
                .count()
            )

        return client_count > 0

    def is_company_exist(self, company_id: uuid.UUID) -> bool:
        with get_session() as db:
            return db.query(Company).filter_by(id=company_id).first() is not None

    def is_name_used(self, name: str, except_id: Optional[str] = None) -> bool:
        with get_session() as db:
            company_count = (
                db.query(Company)
                .filter(Company.name == name, Company.id != except_id)
                .count()
            )

        return company_count > 0

    def get_all_companies_with_employees(self, filter: CompanyFilter) -> List[Company]:
        with get_session() as db:
            query = db.query(Company).options(joinedload(Company.employee))
            query = self.filtered(query, filter)

            # Include companies with `deleted_at` as None
            query = query.filter(Company.deleted_at.is_(None))

            query = query.order_by(Company.created_at.desc())

            if filter.limit:
                query = query.limit(filter.limit)
            if filter.page and filter.limit:
                offset = (filter.page - 1) * filter.limit
                query = query.offset(offset)

            return query.all()

    def get_company_with_employees_by_id(self, company_id: uuid.UUID) -> Optional[Company]:
        with get_session() as db:
            company = (
                db.query(Company)
                .options(joinedload(Company.employee))
                .filter(Company.id == company_id, Company.deleted_at.is_(None))
                .first()
            )
        return company
