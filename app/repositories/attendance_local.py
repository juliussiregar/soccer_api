from datetime import datetime, date
from typing import List
import uuid
from sqlalchemy.orm import joinedload
from sqlalchemy import extract

from app.core.database import get_session
from app.utils.date import get_now
from app.models.attendance_local import AttendanceLocal
from app.schemas.attendance_local_mgt import CreateCheckIn

class AttendanceLocalRepository:

    def get_all_filtered(self, filter_date: date) -> List[AttendanceLocal]:
        with get_session() as db:
            return (
                db.query(AttendanceLocal)
                .options(joinedload(AttendanceLocal.visitor))
                .filter(
                    extract('month', AttendanceLocal.created_at) == filter_date.month,
                    extract('year', AttendanceLocal.created_at) == filter_date.year,
                    extract('day', AttendanceLocal.created_at) == filter_date.day
                )
                .order_by(AttendanceLocal.created_at.desc())
                .all()
            )

    def insert_attendance_checkin(self, payload: CreateCheckIn) -> AttendanceLocal:
        attendance = AttendanceLocal()
        attendance.visitor_id = payload.visitor_id
        attendance.full_name = payload.full_name
        attendance.Check_in = payload.check_in
        attendance.created_at = get_now()

        with get_session() as db:
            db.add(attendance)
            db.flush()
            db.commit()
            db.refresh(attendance)

        return attendance

    def existing_attendance(self, visitor_id: uuid, full_name: str, today_start: datetime) -> AttendanceLocal:
        with get_session() as db:
            ci_status = (
                db.query(AttendanceLocal)
                .filter(AttendanceLocal.visitor_id == visitor_id,
                        AttendanceLocal.full_name == full_name,
                        AttendanceLocal.Check_in >= today_start
                        )
                .first()
            )

        return ci_status

    def existing_attendance_id(self,visitor_id:uuid)->AttendanceLocal:
        with get_session() as db:
            ci_status = (
                db.query(AttendanceLocal)
                .filter(AttendanceLocal.visitor_id == visitor_id
            )
            .first()
            )

        return ci_status

    def delete_attendance_byuser_id(self, visitor_id=uuid) -> AttendanceLocal:
        with get_session() as db:
            ci_status = db.query(AttendanceLocal).filter(AttendanceLocal.visitor_id == visitor_id).delete()
            db.commit()

        return ci_status

    def get_all_visitors(self):
        pass


