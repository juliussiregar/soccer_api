import math
from math import ceil
from typing import List, Tuple, Optional
from datetime import date, datetime, time
import pytz
import uuid
from fastapi import HTTPException

from app.clients.face_api import FaceApiClient
from app.core.constants.app import DEFAULT_TZ
from app.models.attendance import Attendance
from app.repositories.company import CompanyRepository
from app.repositories.daily_salary import DailySalaryRepository
from app.repositories.employee import EmployeeRepository
from app.repositories.employee_daily_salary import EmployeeDailySalaryRepository
from app.repositories.face import FaceRepository
from app.schemas.attendance_mgt import CreateCheckIn, UpdateCheckOut, \
    UpdateAttendance, AttendanceFilter, AttendanceData
from app.repositories.attendance import AttendanceRepository
from app.schemas.employee_daily_salary import CreateNewEmployeeDailySalary
from app.services.employee import EmployeeService
from app.utils.calculate_salary import CalculateSalary
from app.utils.exception import InternalErrorException, UnprocessableException
from app.utils.logger import logger

# Define the default timezone
jakarta_timezone = pytz.timezone(DEFAULT_TZ)

def get_start_of_day(dt: datetime) -> datetime:
    """Helper function to get the start of the current day."""
    return dt.replace(hour=0, minute=0, second=0, microsecond=0)

class AttendanceService:
    def __init__(self) -> None:
        self.calculate_salary_utils = CalculateSalary()
        self.face_api_clients = FaceApiClient()

        self.employee_repo = EmployeeRepository()
        self.attendance_repo = AttendanceRepository()
        self.face_repo = FaceRepository()
        self.company_repo = CompanyRepository()
        self.daily_salary_repo = DailySalaryRepository()
        self.employee_daily_salary_repo = EmployeeDailySalaryRepository()

        self.employee_service = EmployeeService()

    def get_start_of_day(self, dt: datetime) -> datetime:
        """Helper function to get start of the current day in Asia/Jakarta timezone."""
        return dt.astimezone(jakarta_timezone).replace(hour=0, minute=0, second=0, microsecond=0)

    def create_attendance(self, payload):
        try:
            # Validasi apakah company ada
            company = self.company_repo.get_company_by_id(payload.company_id)
            if not company:
                raise HTTPException(status_code=404, detail="Company not found")

            # Validasi apakah employee ada di company tersebut
            employee = self.employee_repo.get_employee_by_id(payload.employee_id)
            if not employee or employee.company_id != payload.company_id:
                raise HTTPException(status_code=404, detail="Employee not found in the specified company")

            # Validasi waktu kerja
            standard_start_time = company.start_time or time(9, 0)
            standard_end_time = company.end_time or time(16, 0)

            # Hitung keterlambatan
            check_in_time = payload.check_in.time()
            late_minutes = 0
            if check_in_time > standard_start_time:
                late_minutes = math.ceil((datetime.combine(date.today(), check_in_time) -
                                          datetime.combine(date.today(), standard_start_time)).total_seconds() / 60)

            # Hitung lembur
            overtime_minutes = 0
            if payload.check_out:
                check_out_time = payload.check_out.astimezone(jakarta_timezone).time()
                if check_out_time > standard_end_time:
                    overtime_minutes = math.ceil((datetime.combine(date.today(), check_out_time) -
                                                  datetime.combine(date.today(),
                                                                   standard_end_time)).total_seconds() / 60)

            # Konversi keterlambatan dan lembur ke jam dan menit
            late_hours = late_minutes // 60
            late_remaining_minutes = late_minutes % 60
            overtime_hours = overtime_minutes // 60
            overtime_remaining_minutes = overtime_minutes % 60

            # Buat deskripsi
            description = (
                f"Checked in with {late_hours} hours {late_remaining_minutes} minutes late and "
                f"Checked out with {overtime_hours} hours {overtime_remaining_minutes} minutes overtime."
            )
            logger.info(f"Description: {description}")

            # Update payload
            payload.late = late_minutes
            payload.overtime = overtime_minutes
            payload.description = description

            # Insert attendance
            new_attendance = self.attendance_repo.insert_attendance(payload)

            # Perhitungan salary jika ada data salary harian
            daily_salary = self.daily_salary_repo.get_by_employee_id(payload.employee_id)
            # if daily_salary:
            #     salary_data = self.calculate_salary_utils.calculate_daily_salary(
            #         new_attendance, daily_salary, late_minutes, overtime_minutes
            #     )

            company = self.company_repo.get_company_by_employee_id(payload.employee_id)
            if company and daily_salary:
                salary_data = self.calculate_salary_utils.calculate_daily_salary(new_attendance, company,
                                                                                 late_minutes, daily_salary)
                # Buat payload salary
                new_salary_payload = CreateNewEmployeeDailySalary(
                    employee_id=payload.employee_id,
                    work_date=new_attendance.check_in.date(),
                    hours_worked=round(salary_data["hours_worked"], 2),
                    late_deduction=round(salary_data["late_deduction"], 2),
                    month=new_attendance.check_in.month,
                    year=new_attendance.check_in.year,
                    normal_salary=round(salary_data["normal_salary"], 2),
                    total_salary=round(salary_data["total_salary"], 2),
                )

                # Masukkan data salary
                self.employee_daily_salary_repo.insert(new_salary_payload)
                logger.info("Inserted new salary data for create_attendance.")

            return new_attendance
        except Exception as err:
            logger.error(str(err))
            raise InternalErrorException("Failed to create attendance.")

    def update_attendance(self, attendance_id: int, payload: UpdateAttendance):
        try:
            return self.attendance_repo.update_attendance(attendance_id, payload)
        except Exception as err:
            logger.error(str(err))
            raise InternalErrorException("Failed to update attendance.")

    def delete_attendance(self, attendance_id: int):
        try:
            # Cek apakah attendance dengan ID diberikan ada
            check_employee_id_by_attendance_id = self.attendance_repo.get_attendance_by_id(attendance_id)

            if not check_employee_id_by_attendance_id:
                # logger.error(f"Attendance with ID {attendance_id} not found.")
                raise HTTPException(status_code=404, detail=f"Attendance with ID {attendance_id} not found.")

            # Ambil employee_id dari attendance
            employee_id = check_employee_id_by_attendance_id.employee_id

            # logger.info(f"Attendance found: {check_employee_id_by_attendance_id}")
            # logger.info(f"Employee ID: {employee_id}")

            # Cek apakah ada data gaji harian terkait employee ini
            check_employee_daily_salary = self.employee_daily_salary_repo.get_by_employee_id(employee_id)

            if check_employee_daily_salary:
                self.employee_daily_salary_repo.delete_employee_daily_salary_by_employee_id(employee_id)

            # Hapus attendance
            return self.attendance_repo.delete_attendance(attendance_id)
        except HTTPException as http_err:
            raise http_err
        except Exception as err:
            logger.error(str(err))
            raise InternalErrorException("Failed to delete attendance.")

    def list_attendances(self, filter: AttendanceFilter) -> Tuple[List[AttendanceData], int, int]:
        attendances = self.attendance_repo.get_all_filtered(filter)
        total_rows = self.attendance_repo.count_by_filter(filter)
        total_pages = (total_rows + filter.limit - 1) // filter.limit if filter.limit else 1
        return attendances, total_rows, total_pages

    def list_attendances_by_date(
            self, filter_date: date, company_id: Optional[uuid.UUID], search: Optional[str]
    ):
        """Retrieve attendances filtered by date, optional company_id, and search query."""
        attendances, total_records, total_pages = self.attendance_repo.get_attendances_by_date(
            filter_date, company_id, search
        )
        return attendances, total_records, total_pages

    def list_attendances_by_month(
        self,
        year: int,
        month: int,
        company_id: Optional[uuid.UUID],
        employee_id: Optional[uuid.UUID],
        limit: int,
        page: int,
        search: Optional[str]
    ):
        """
        Retrieve attendances filtered by month, year, optional company_id, optional employee_id, and search query.
        """
        attendances, total_records, total_pages = self.attendance_repo.get_attendances_by_month(
            year=year,
            month=month,
            company_id=company_id,
            employee_id=employee_id,
            limit=limit,
            page=page,
            search=search
        )
        return attendances, total_records, total_pages


    def list_attendances_by_company(self, company_id: Optional[uuid.UUID], limit: int, page: int) -> Tuple[
        List[Attendance], int, int]:
        total_records = self.attendance_repo.count_attendances_by_company(company_id)
        total_pages = ceil(total_records / limit)

        attendances = self.attendance_repo.get_all_by_company(company_id, limit, (page - 1) * limit)
        return attendances, total_records, total_pages

    def create_check_in(self, payload: CreateCheckIn) -> Attendance:
        # Convert check_in to Asia/Jakarta timezone
        check_in_time = payload.check_in.astimezone(jakarta_timezone)
        today_start = self.get_start_of_day(datetime.now(jakarta_timezone))
        existing_attendance = self.attendance_repo.existing_attendance(payload.employee_id, today_start)

        if existing_attendance:
            raise UnprocessableException("Employee has already checked in today and has not checked out yet.")

        try:
            # Update payload's check_in with Jakarta timezone
            payload.check_in = check_in_time
            new_attendance = self.attendance_repo.insert_attendance_checkin(payload)
        except Exception as err:
            logger.error(str(err))
            raise InternalErrorException("Failed to create check-in.")

        return new_attendance

    def update_check_out(self, payload: UpdateCheckOut) -> Attendance:
        # Validasi apakah company ada
        company = self.company_repo.get_company_by_id(payload.company_id)
        if not company:
            raise HTTPException(status_code=404, detail="Company not found")

        # Validasi apakah employee ada di company tersebut
        employee = self.employee_repo.get_employee_by_id(payload.employee_id)
        if not employee or employee.company_id != payload.company_id:
            raise HTTPException(status_code=404, detail="Employee not found in the specified company")

        # Validasi apakah employee telah melakukan check-in hari ini
        today_start = self.get_start_of_day(datetime.now(jakarta_timezone))
        existing_attendance = self.attendance_repo.existing_attendance(payload.employee_id, today_start)
        if not existing_attendance:
            raise UnprocessableException("Employee has not checked in today.")

        # Validasi dan hitung waktu check-out
        check_out_time = payload.check_out.astimezone(jakarta_timezone)
        standard_start_time = company.start_time or time(9, 0)
        standard_end_time = company.end_time or time(17, 0)

        check_in_time = existing_attendance.check_in.astimezone(jakarta_timezone).time()
        check_out_time_only = check_out_time.time()

        # Logging untuk debug waktu
        logger.info(f"Check-in time: {check_in_time}, Check-out time: {check_out_time_only}")
        logger.info(f"Standard working hours: {standard_start_time} to {standard_end_time}")

        # Hitung keterlambatan dan lembur
        late_minutes = 0
        if check_in_time > standard_start_time:
            late_minutes = (datetime.combine(date.today(), check_in_time) - datetime.combine(date.today(),
                                                                                             standard_start_time)).seconds // 60

        overtime_minutes = 0
        if check_out_time_only > standard_end_time:
            overtime_minutes = (datetime.combine(date.today(), check_out_time_only) - datetime.combine(date.today(),
                                                                                                       standard_end_time)).seconds // 60

        # Convert keterlambatan dan lembur ke format jam dan menit
        late_hours = late_minutes // 60
        late_remaining_minutes = late_minutes % 60
        overtime_hours = overtime_minutes // 60
        overtime_remaining_minutes = overtime_minutes % 60

        # Buat deskripsi
        description = (
            f"Checked in with {late_hours} hours {late_remaining_minutes} minutes late and "
            f"Checked out with {overtime_hours} hours {overtime_remaining_minutes} minutes overtime."
        )
        logger.info(f"Description: {description}")

        # Update check-out di attendance
        try:
            payload.check_out = check_out_time
            updated_attendance = self.attendance_repo.update_attendance_checkout(
                payload, late_minutes, overtime_minutes, description
            )

            # Periksa apakah ada data gaji harian
            daily_salary = self.daily_salary_repo.get_by_employee_id(payload.employee_id)
            # if daily_salary:
            #     salary_data = self.calculate_salary_utils.calculate_daily_salary(updated_attendance, daily_salary, late_minutes)

            company = self.company_repo.get_company_by_employee_id(payload.employee_id)
            if company and daily_salary:
                salary_data = self.calculate_salary_utils.calculate_daily_salary(updated_attendance, company, late_minutes, daily_salary)

                # Buat payload untuk data gaji harian
                new_salary_payload = CreateNewEmployeeDailySalary(
                    employee_id=payload.employee_id,
                    work_date=today_start.date(),
                    hours_worked=salary_data["hours_worked"],
                    late_deduction=salary_data["late_deduction"],
                    month=today_start.month,
                    year=today_start.year,
                    normal_salary=salary_data["normal_salary"],
                    total_salary=salary_data["total_salary"],
                )

                # Cek jika data gaji sudah ada, jika belum masukkan data baru
                existing_salary = self.employee_daily_salary_repo.get_by_employee_id_and_date(
                    payload.employee_id, today_start.date()
                )
                if not existing_salary:
                    self.employee_daily_salary_repo.insert(new_salary_payload)
                    logger.info("Inserted new salary data.")
                else:
                    logger.info("Salary data already exists, skipping insertion.")

        except Exception as err:
            logger.error(f"Error during check-out update: {err}")
            raise InternalErrorException("Failed to update check-out or calculate daily salary.")

        return updated_attendance