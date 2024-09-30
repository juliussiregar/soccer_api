from datetime import datetime,date
from typing import List, Optional, Tuple
import uuid
from passlib.context import CryptContext
from sqlalchemy.orm import Query, joinedload
from sqlalchemy import extract, insert

from app.core.database import get_session
from app.schemas.visitor import VisitorFilter
from app.utils.date import get_now
from app.utils.etc import id_generator
from app.models.attendance import Attendance
from app.schemas.attendance_mgt import AttendanceFilter, CreateCheckIn,UpdateCheckOut

from app.utils.exception import UnprocessableException



class AttendanceRepository :


    def get_all_filtered(self, filter_date: date) -> List[Attendance]:
        with get_session() as db:
            return (
                db.query(Attendance)
                .options(joinedload(Attendance.visitor))
                .filter(
                        extract('month', Attendance.created_at) == filter_date.month,
                        extract('year', Attendance.created_at) == filter_date.year,
                        extract('day', Attendance.created_at) == filter_date.day
                        )
                .order_by(Attendance.created_at.desc())
                .all()
            )


    def insert_attendance_checkin(self,payload:CreateCheckIn)->Attendance:
        attendance = Attendance()
        attendance.client_id = payload.client_id
        attendance.visitor_id = payload.visitor_id
        attendance.Check_in = payload.check_in
        attendance.created_at = get_now()

        with get_session() as db:
            db.add(attendance)
            db.flush()
            db.commit()
            db.refresh(attendance)

        return attendance

    def update_attendance_checkout(self,payload:UpdateCheckOut)->Attendance:
        with get_session() as db:
            ci_status = (
                db.query(Attendance)
                .filter(Attendance.visitor_id == payload.visitor_id,
                Attendance.Check_out == None  # Belum check-out
            )
            .first()
            )

            if ci_status:
                ci_status.Check_out = payload.check_out
                ci_status.updated_at = get_now()
                db.commit()
                db.refresh(ci_status)

        return ci_status

    def existing_attendance(self,visitor_id:uuid,today_start:datetime)->Attendance:
        with get_session() as db:
            ci_status = (
                db.query(Attendance)
                .filter(Attendance.visitor_id == visitor_id,
                Attendance.Check_in >= today_start,
                Attendance.Check_out == None  # Belum check-out
            )
            .first()
            )

        return ci_status
    
    def existing_attendance_id(self,visitor_id:uuid)->Attendance:
        with get_session() as db:
            ci_status = (
                db.query(Attendance)
                .filter(Attendance.visitor_id == visitor_id,
                        Attendance.Check_out == None
            )
            .first()
            )

        return ci_status
    
    def delete_attendance_byuser_id(self,visitor_id=uuid)->Attendance:
        with get_session() as db:
            ci_status = db.query(Attendance).filter(Attendance.visitor_id == visitor_id).delete()
            db.commit()

        return ci_status

    
