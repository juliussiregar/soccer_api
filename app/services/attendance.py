from typing import List, Tuple
from datetime import date, datetime, timedelta

import pytz
from app.services.visitor import VisitorService
from app.schemas.visitor import CreateNewVisitor,Face,GetVisitor,IdentifyVisitorFace,IdentifyVisitor, VisitorFilter
from app.schemas.faceapi_mgt import CreateEnrollFace,IdentifyFace
from app.repositories.attendance import AttendanceRepository
from app.schemas.attendance_mgt import CreateCheckIn,UpdateCheckOut
from app.models.client import Client
from app.models.visitor import Visitor
from app.models.attendance import Attendance
from app.models.face import Faces
from app.core.constants.information import CLIENT_NAME


from app.utils.date import get_now
from app.utils.exception import InternalErrorException, UnprocessableException
from app.utils.logger import logger


class AttendanceService:
    def __init__(self) -> None:
        self.visitor_service = VisitorService()
        self.attendance_repo = AttendanceRepository()

    def get_start_of_day(self,dt: datetime):
        """Helper function to get start of the current day."""
        return dt.replace(hour=0, minute=0, second=0, microsecond=0)
    
    def list(self,filter_date:date)->Tuple[Attendance,Visitor]:
        visitors_today = self.attendance_repo.get_all_filtered(filter_date)
        return visitors_today

    def create(self,payload:IdentifyVisitor)->Tuple[Visitor,List[Attendance]]:
        identify_visitor = self.visitor_service.identify_face_visitor(payload)
        today_start = self.get_start_of_day(datetime.utcnow())
        existing_attendance_today = self.attendance_repo.existing_attendance(identify_visitor.id,today_start)
        existing_by_id = self.attendance_repo.existing_attendance_id(identify_visitor.id)
        if existing_by_id:
            if existing_attendance_today:
            # Jika sudah check-in tapi belum check-out, berikan error
                raise UnprocessableException(f"Visitor {identify_visitor.username} has already checked in and has not checked out yet.")
            attendance_check_out = UpdateCheckOut(
                visitor_id=identify_visitor.id,
                client_id=identify_visitor.client_id,
                check_out=self.get_start_of_day(datetime.utcnow() - timedelta(days=1)) + timedelta(hours=23, minutes=59)
            )
            self.attendance_repo.update_attendance_checkout(attendance_check_out)

        try:
            attendance_check_in = CreateCheckIn(
                visitor_id=identify_visitor.id,
                client_id=identify_visitor.client_id,
                check_in=datetime.now(pytz.timezone('Asia/Jakarta'))
            )
            new_attendance = self.attendance_repo.insert_attendance_checkin(attendance_check_in)
        except Exception as err:
            err_msg = str(err)
            logger.error(err_msg)
            raise InternalErrorException(err_msg)
        
        return new_attendance,identify_visitor
    
    def update(self,payload:IdentifyVisitor)->Tuple[Visitor,List[Attendance]]:
        identify_visitor = self.visitor_service.identify_face_visitor(payload)
        today_start = self.get_start_of_day(datetime.utcnow())
        existing_attendance = self.attendance_repo.existing_attendance(identify_visitor.id,today_start)

        if not existing_attendance:
            # Jika belum check-in, berikan error
            raise UnprocessableException(f"Visitor {identify_visitor.username} has not checked in yet.")
        
        try:
            attendance_check_out = UpdateCheckOut(
                visitor_id=identify_visitor.id,
                client_id=identify_visitor.client_id,
                check_out=datetime.now(pytz.timezone('Asia/Jakarta'))
            )
            update_attendance = self.attendance_repo.update_attendance_checkout(attendance_check_out)
        except Exception as err:
            err_msg = str(err)
            logger.error(err_msg)
            raise InternalErrorException(err_msg)
        
        return update_attendance,identify_visitor