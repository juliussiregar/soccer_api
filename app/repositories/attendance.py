from datetime import datetime, date
from typing import List, Optional
import uuid
from sqlalchemy.orm import joinedload
from sqlalchemy import extract

from app.core.database import get_session
from app.models.attendance import Attendance
from app.schemas.attendance_mgt import CreateCheckIn, UpdateCheckOut
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
