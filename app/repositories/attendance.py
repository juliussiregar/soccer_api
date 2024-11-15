from datetime import datetime, date
from typing import List, Optional, Tuple
import uuid
from sqlalchemy.orm import joinedload
from sqlalchemy import extract

from app.core.database import get_session
from app.models.attendance import Attendance
from app.schemas.attendance_mgt import CreateCheckIn, UpdateCheckOut, CreateAttendance, UpdateAttendance
from app.utils.date import get_now

class AttendanceRepository:

    def get_all_filtered(self, filter_date: date) -> List[Attendance]:
        with get_session() as db:
            return (
                db.query(Attendance)
                .options(joinedload(Attendance.employee), joinedload(Attendance.company))
                .filter(
                    extract('month', Attendance.created_at) == filter_date.month,
                    extract('year', Attendance.created_at) == filter_date.year,
                    extract('day', Attendance.created_at) == filter_date.day
                )
                .order_by(Attendance.created_at.desc())
                .all()
            )

    def insert_attendance(self, payload: CreateAttendance) -> Attendance:
        attendance = Attendance(
            company_id=payload.company_id,
            employee_id=payload.employee_id,
            check_in=payload.check_in,
            check_out=payload.check_out,
            photo_in=payload.photo_in,
            photo_out=payload.photo_out,
            location=payload.location,
            type=payload.type,
            late=payload.late,
            overtime=payload.overtime,
            description=payload.description,
            created_at=get_now(),
        )

        with get_session() as db:
            db.add(attendance)
            db.flush()
            db.commit()
            db.refresh(attendance)

        return attendance

    def update_attendance(self, attendance_id: int, payload: UpdateAttendance) -> Optional[Attendance]:
        with get_session() as db:
            attendance = db.query(Attendance).filter(Attendance.id == attendance_id).first()

            if not attendance:
                return None

            if payload.company_id:
                attendance.company_id = payload.company_id
            if payload.employee_id:
                attendance.employee_id = payload.employee_id
            if payload.check_in:
                attendance.check_in = payload.check_in
            if payload.check_out:
                attendance.check_out = payload.check_out
            if payload.photo_in:
                attendance.photo_in = payload.photo_in
            if payload.photo_out:
                attendance.photo_out = payload.photo_out
            if payload.location:
                attendance.location = payload.location
            if payload.type:
                attendance.type = payload.type
            if payload.late is not None:
                attendance.late = payload.late
            if payload.overtime is not None:
                attendance.overtime = payload.overtime
            if payload.description:
                attendance.description = payload.description

            attendance.updated_at = get_now()
            db.commit()
            db.refresh(attendance)

        return attendance

    def delete_attendance(self, attendance_id: int) -> Optional[Attendance]:
        with get_session() as db:
            attendance = db.query(Attendance).filter(Attendance.id == attendance_id).first()
            if not attendance:
                return None

            db.delete(attendance)
            db.commit()

        return attendance

    def get_all_attendances(
            self, company_id: Optional[uuid.UUID], limit: int, page: int
    ) -> Tuple[List[Attendance], int, int]:
        with get_session() as db:
            query = db.query(Attendance).options(joinedload(Attendance.employee), joinedload(Attendance.company))

            if company_id:
                query = query.filter(Attendance.company_id == company_id)

            total_records = query.count()
            total_pages = (total_records + limit - 1) // limit

            query = query.limit(limit).offset((page - 1) * limit).all()

        return query, total_records, total_pages

    def get_all_by_company(self, company_id: uuid.UUID, limit: int, offset: int) -> List[Attendance]:
        with get_session() as db:
            return (
                db.query(Attendance)
                .filter(Attendance.company_id == company_id)
                .limit(limit)
                .offset(offset)
                .all()
            )

    def count_attendances_by_company(self, company_id: uuid.UUID) -> int:
        with get_session() as db:
            return db.query(Attendance).filter(Attendance.company_id == company_id).count()

    def get_all_by_date(self, filter_date: date, limit: int, offset: int) -> List[Attendance]:
        with get_session() as db:
            return (
                db.query(Attendance)
                .filter(
                    extract('month', Attendance.created_at) == filter_date.month,
                    extract('year', Attendance.created_at) == filter_date.year,
                    extract('day', Attendance.created_at) == filter_date.day
                )
                .order_by(Attendance.created_at.desc())
                .limit(limit)
                .offset(offset)
                .all()
            )

    def count_attendances_by_date(self, filter_date: date) -> int:
        with get_session() as db:
            return (
                db.query(Attendance)
                .filter(
                    extract('month', Attendance.created_at) == filter_date.month,
                    extract('year', Attendance.created_at) == filter_date.year,
                    extract('day', Attendance.created_at) == filter_date.day
                )
                .count()
            )

    def get_all_by_month(self, month: int, year: int, limit: int, offset: int) -> List[Attendance]:
        with get_session() as db:
            return (
                db.query(Attendance)
                .filter(
                    extract('month', Attendance.created_at) == month,
                    extract('year', Attendance.created_at) == year
                )
                .limit(limit)
                .offset(offset)
                .all()
            )

    def count_attendances_by_month(self, month: int, year: int) -> int:
        with get_session() as db:
            return (
                db.query(Attendance)
                .filter(
                    extract('month', Attendance.created_at) == month,
                    extract('year', Attendance.created_at) == year
                )
                .count()
            )

    def insert_attendance_checkin(self, payload: CreateCheckIn) -> Attendance:
        attendance = Attendance(
            company_id=payload.company_id,
            employee_id=payload.employee_id,
            check_in=payload.check_in,
            photo_in=payload.photo_in,
            location=payload.location,
            type=payload.type if payload.type else "WFO",  # Default ke WFO jika tidak ada
            created_at=get_now()
        )

        with get_session() as db:
            db.add(attendance)
            db.flush()
            db.commit()
            db.refresh(attendance)

        return attendance

    def update_attendance_checkout(self, payload: UpdateCheckOut, late_minutes: int, overtime_minutes: int, description: str) -> Optional[Attendance]:
        with get_session() as db:
            attendance = (
                db.query(Attendance)
                .filter(Attendance.employee_id == payload.employee_id, Attendance.check_out == None)
                .first()
            )

            if attendance:
                attendance.check_out = payload.check_out
                attendance.photo_out = payload.photo_out
                attendance.location = payload.location  # Lokasi check-out
                attendance.late = late_minutes
                attendance.overtime = overtime_minutes
                attendance.description = description
                attendance.updated_at = get_now()
                db.commit()
                db.refresh(attendance)

        return attendance

    def existing_attendance(self, employee_id: uuid.UUID, today_start: datetime) -> Optional[Attendance]:
        with get_session() as db:
            return (
                db.query(Attendance)
                .filter(
                    Attendance.employee_id == employee_id,
                    Attendance.check_in >= today_start,
                    Attendance.check_out == None
                )
                .first()
            )

    def get_attendances_by_date(
            self, filter_date: date, company_id: Optional[uuid.UUID]
    ) -> Tuple[List[Attendance], int, int]:
        """Retrieve attendances filtered by specific date and optional company_id."""
        with get_session() as db:
            query = db.query(Attendance).options(joinedload(Attendance.employee), joinedload(Attendance.company))

            if company_id:
                query = query.filter(Attendance.company_id == company_id)

            query = query.filter(
                extract('year', Attendance.created_at) == filter_date.year,
                extract('month', Attendance.created_at) == filter_date.month,
                extract('day', Attendance.created_at) == filter_date.day
            )

            total_records = query.count()
            query = query.order_by(Attendance.created_at.desc()).all()

        return query, total_records, 1  # By-date filtering doesn't need pagination

    def get_attendances_by_month(
            self, year: int, month: int, company_id: Optional[uuid.UUID], limit: int, page: int
    ) -> Tuple[List[Attendance], int, int]:
        """Retrieve attendances filtered by year, month, and optional company_id."""
        with get_session() as db:
            query = db.query(Attendance).options(joinedload(Attendance.employee), joinedload(Attendance.company))

            if company_id:
                query = query.filter(Attendance.company_id == company_id)

            query = query.filter(
                extract('year', Attendance.created_at) == year,
                extract('month', Attendance.created_at) == month
            )

            total_records = query.count()
            total_pages = (total_records + limit - 1) // limit
            query = query.order_by(Attendance.created_at.desc()).limit(limit).offset((page - 1) * limit).all()

        return query, total_records, total_pages
