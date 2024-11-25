# repositories/application.py

from typing import List, Optional
import uuid
from sqlalchemy.orm import Query
from app.core.database import get_session
from app.models.application import Application
from app.schemas.application import CreateNewApplication, UpdateApplication, ApplicationFilter
from sqlalchemy.orm import joinedload
from datetime import datetime, timezone

class ApplicationRepository:
    
    def get_application_by_id(self, application_id: int) -> Optional[Application]:
        with get_session() as db:
            return db.query(Application).filter(Application.id == application_id).first()

    def filtered(self, query: Query, filter: ApplicationFilter) -> Query:
        if filter.employee_id:
            query = query.filter(Application.employee_id == filter.employee_id)
        if filter.company_id:
            query = query.join(Application.employee).filter(Application.employee.has(company_id=filter.company_id))
        return query

    def get_all_filtered(self, filter: ApplicationFilter) -> List[Application]:
        with get_session() as db:
            query = db.query(Application).options(joinedload(Application.employee))
            query = self.filtered(query, filter).order_by(Application.created_at.desc())
            if filter.limit:
                query = query.limit(filter.limit)
            if filter.page and filter.limit:
                offset = (filter.page - 1) * filter.limit
                query = query.offset(offset)
            return query.all()

    def count_by_filter(self, filter: ApplicationFilter) -> int:
        with get_session() as db:
            query = db.query(Application)
            query = self.filtered(query, filter)
            return query.count()

    def insert(self, payload: CreateNewApplication) -> Application:
        application = Application(
            employee_id=payload.employee_id,
            location=payload.location,
            status=payload.status,
            description=payload.description
        )
        with get_session() as db:
            db.add(application)
            db.flush()
            db.commit()
            db.refresh(application)
        return application

    def update(self, application_id: int, payload: UpdateApplication) -> Optional[Application]:
        with get_session() as db:
            application = db.query(Application).filter(Application.id == application_id).first()
            if not application:
                return None
            for key, value in payload.dict(exclude_unset=True).items():
                setattr(application, key, value)
            application.updated_at = datetime.now(timezone.utc)
            db.commit()
            db.refresh(application)
        return application

    def delete_application_by_id(self, application_id: int) -> Optional[Application]:
        with get_session() as db:
            application = db.query(Application).filter(Application.id == application_id).first()
            if application:
                db.delete(application)
                db.commit()
            return application

    def get_by_employee_id(self, employee_id: uuid.UUID) -> Optional[Application]:
        with get_session() as db:
            return db.query(Application).filter(Application.employee_id == employee_id).first()

    def delete_application_by_employee_id(self, employee_id: uuid.UUID) -> Optional[Application]:
        with get_session() as db:
            application = db.query(Application).filter(Application.employee_id == employee_id).delete()
            db.commit()

        return application
