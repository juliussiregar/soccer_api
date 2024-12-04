from datetime import datetime, date
from typing import List, Optional, Tuple
import uuid

from fastapi import Query
from sqlalchemy.orm import joinedload
from sqlalchemy import extract, or_

from app.core.database import get_session
from app.models.attendance import Attendance
from app.models.employee import Employee
from app.schemas.attendance_mgt import CreateCheckIn, UpdateCheckOut, CreateAttendance, UpdateAttendance, \
    AttendanceFilter
from app.utils.date import get_now

class AttendanceRepository:

    def filtered(self, query: Query, filter: AttendanceFilter) -> Query:
        if filter.search:
            query = query.join(Attendance.employee).filter(Employee.user_name.contains(filter.search))
        if filter.company_id:
            query = query.filter(Attendance.company_id == filter.company_id)
        return query

    def get_all_filtered(self, filter: AttendanceFilter) -> List[Attendance]:
        with get_session() as db:
            query = db.query(Attendance).options(joinedload(Attendance.employee), joinedload(Attendance.company))
            query = self.filtered(query, filter).order_by(Attendance.created_at.desc())
            if filter.limit:
                query = query.limit(filter.limit)
            if filter.page and filter.limit:
                offset = (filter.page - 1) * filter.limit
                query = query.offset(offset)
            return query.all()

    def count_by_filter(self, filter: AttendanceFilter) -> int:
        with get_session() as db:
            query = db.query(Attendance)
            query = self.filtered(query, filter)
            return query.count()

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
            description=payload.description
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

    def delete_attendance_by_employee_id(self, employee_id: uuid.UUID) -> Optional[Attendance]:
        with get_session() as db:
            attendance = db.query(Attendance).filter(Attendance.employee_id == employee_id).delete()
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

    def get_attendances_by_date(
            self, filter_date: date, company_id: Optional[uuid.UUID], search: Optional[str]
    ) -> Tuple[List[Attendance], int, int]:
        """Retrieve attendances filtered by specific date, optional company_id, and search query."""
        with get_session() as db:
            query = db.query(Attendance).options(
                joinedload(Attendance.employee), joinedload(Attendance.company)
            )

            if company_id:
                query = query.filter(Attendance.company_id == company_id)

            query = query.filter(
                extract('year', Attendance.created_at) == filter_date.year,
                extract('month', Attendance.created_at) == filter_date.month,
                extract('day', Attendance.created_at) == filter_date.day
            )

            if search:
                search_filter = f"%{search}%"
                query = query.filter(
                    or_(
                        Attendance.employee.has(Employee.user_name.ilike(search_filter)),
                        Attendance.description.ilike(search_filter),
                    )
                )

            total_records = query.count()
            query = query.order_by(Attendance.created_at.desc()).all()

        total_pages = 1  # Default 1 page as there is no pagination
        return query, total_records, total_pages

    def get_attendances_by_month(
        self,
        year: int,
        month: int,
        company_id: Optional[uuid.UUID],
        employee_id: Optional[uuid.UUID],
        limit: int,
        page: int,
        search: Optional[str]
    ) -> Tuple[List[Attendance], int, int]:
        """
        Retrieve attendances filtered by year, month, optional company_id, employee_id, and search query.
        """
        with get_session() as db:
            query = db.query(Attendance).options(
                joinedload(Attendance.employee), joinedload(Attendance.company)
            )

            # Filter by company_id if provided
            if company_id:
                query = query.filter(Attendance.company_id == company_id)

            # Filter by employee_id if provided
            if employee_id:
                query = query.filter(Attendance.employee_id == employee_id)

            # Filter by year and month
            query = query.filter(
                extract('year', Attendance.created_at) == year,
                extract('month', Attendance.created_at) == month
            )

            # Apply search filter if provided
            if search:
                search_filter = f"%{search}%"
                query = query.filter(
                    or_(
                        Attendance.employee.has(Employee.user_name.ilike(search_filter)),
                        Attendance.description.ilike(search_filter),
                    )
                )

            # Get total records and calculate total pages
            total_records = query.count()
            total_pages = (total_records + limit - 1) // limit

            # Apply ordering, pagination, and execute query
            attendances = query.order_by(Attendance.created_at.desc()).limit(limit).offset((page - 1) * limit).all()

        return attendances, total_records, total_pages


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

    def existing_attendance_today(self, employee_id: uuid.UUID, today_start: datetime, today_end: datetime) -> Optional[Attendance]:
        with get_session() as db:
            return (
                db.query(Attendance)
                .filter(
                    Attendance.employee_id == employee_id,
                    Attendance.check_in >= today_start,
                    Attendance.check_out <= today_end
                )
                .first()
            )

    def get_last_attendance_by_employee_id(self, employee_id: uuid.UUID) -> Optional[Attendance]:
        """Get the most recent attendance record by employee_id."""
        with get_session() as db:
            last_attendance = (
                db.query(Attendance)
                .filter(Attendance.employee_id == employee_id)
                .order_by(Attendance.check_in.desc(), Attendance.check_out.desc())
                .first()
            )
            return last_attendance

    def get_attendance_by_id(self, attendance_id: int) -> Optional[Attendance]:
        with get_session() as db:
            attendance = db.query(Attendance).filter(Attendance.id == attendance_id).options(joinedload(Attendance.employee), joinedload(Attendance.company)).first()
        return attendance