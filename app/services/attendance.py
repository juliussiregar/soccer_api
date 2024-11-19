import base64
from decimal import Decimal, ROUND_DOWN
from io import BytesIO
from math import ceil
from typing import List, Tuple, Optional
from datetime import date, datetime, time, timedelta

import face_recognition
import numpy as np
import pytz
import uuid

from PIL import Image
from fastapi import HTTPException
from sqlalchemy import Row

from app.clients.face_api import FaceApiClient
from app.core.constants.app import DEFAULT_TZ
from app.core.constants.information import CLIENT_NAME
from app.models.attendance import Attendance
from app.models.employee import Employee
from app.models.employee_daily_salary import EmployeeDailySalary
from app.models.face import Face
from app.repositories.company import CompanyRepository
from app.repositories.daily_salary import DailySalaryRepository
from app.repositories.employee import EmployeeRepository
from app.repositories.employee_daily_salary import EmployeeDailySalaryRepository
from app.repositories.face import FaceRepository
from app.schemas.attendance_mgt import CreateCheckIn, UpdateCheckOut, IdentifyEmployee, CreateAttendance, \
    UpdateAttendance
from app.repositories.attendance import AttendanceRepository
from app.schemas.employee_daily_salary import CreateNewEmployeeDailySalary
from app.schemas.faceapi_mgt import IdentifyFace
from app.services.employee import EmployeeService
from app.utils.date import get_now
from app.utils.exception import InternalErrorException, UnprocessableException
from app.utils.logger import logger

# Define the default timezone
jakarta_timezone = pytz.timezone(DEFAULT_TZ)

def get_start_of_day(dt: datetime) -> datetime:
    """Helper function to get the start of the current day."""
    return dt.replace(hour=0, minute=0, second=0, microsecond=0)

class AttendanceService:
    def __init__(self) -> None:
        self.face_api_clients = FaceApiClient()

        self.employee_repo = EmployeeRepository()
        self.attendance_repo = AttendanceRepository()
        self.face_repo = FaceRepository()
        self.company_repo = CompanyRepository()
        self.daily_salary_repo = DailySalaryRepository()
        self.employee_daily_salary_repo = EmployeeDailySalaryRepository()

        self.employee_service = EmployeeService()

    def process_base64_image(self, base64_string: str) -> np.ndarray:
        """Convert base64 string to numpy array in RGB format."""
        try:
            # Remove potential data URI prefix
            if 'base64,' in base64_string:
                base64_string = base64_string.split('base64,')[1]

            img_data = base64.b64decode(base64_string)
            img = Image.open(BytesIO(img_data)).convert('RGB')
            return np.array(img)
        except Exception as e:
            logger.error(f"Error processing base64 image: {str(e)}")
            raise HTTPException(status_code=400, detail=f"Invalid image format: {str(e)}")

    def get_face_encoding(self, img_array: np.ndarray) -> np.ndarray:
        """Generate face encoding from an RGB image array."""
        face_locations = face_recognition.face_locations(img_array)

        if not face_locations:
            raise HTTPException(status_code=400, detail="No face detected in the image")

        return face_recognition.face_encodings(img_array, face_locations)[0]

    def row_to_dict(self, row: Row) -> dict:
        """Convert SQLAlchemy Row to dictionary."""
        try:
            return {key: getattr(row, key) for key in row._fields}
        except Exception as e:
            logger.error(f"Error converting row to dict: {str(e)}")
            return {}

    def get_start_of_day(self, dt: datetime) -> datetime:
        """Helper function to get start of the current day in Asia/Jakarta timezone."""
        return dt.astimezone(jakarta_timezone).replace(hour=0, minute=0, second=0, microsecond=0)

    def create_attendance(self, payload: CreateAttendance):
        try:
            return self.attendance_repo.insert_attendance(payload)
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
            return self.attendance_repo.delete_attendance(attendance_id)
        except Exception as err:
            logger.error(str(err))
            raise InternalErrorException("Failed to delete attendance.")

    def list_attendances(
            self, company_id: Optional[uuid.UUID], limit: int, page: int
    ) -> Tuple[List[dict], int, int]:
        try:
            return self.attendance_repo.get_all_attendances(company_id, limit, page)
        except Exception as err:
            logger.error(str(err))
            raise InternalErrorException("Failed to list attendances.")

    def list_attendances_by_date(self, filter_date: date, company_id: Optional[uuid.UUID]):
        """Retrieve attendances filtered by date and optional company_id."""
        attendances, total_records, total_pages = self.attendance_repo.get_attendances_by_date(
            filter_date, company_id
        )
        return attendances, total_records, total_pages

    def list_attendances_by_month(
        self, year: int, month: int, company_id: Optional[uuid.UUID], limit: int, page: int
    ):
        """Retrieve attendances filtered by month, year, and optional company_id."""
        attendances, total_records, total_pages = self.attendance_repo.get_attendances_by_month(
            year, month, company_id, limit, page
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
            f"Checked out with {late_hours} hours {late_remaining_minutes} minutes late and "
            f"{overtime_hours} hours {overtime_remaining_minutes} minutes overtime."
        )
        logger.info(f"Description: {description}")

        # Update check-out di attendance
        try:
            payload.check_out = check_out_time
            updated_attendance = self.attendance_repo.update_attendance_checkout(
                payload, late_minutes, overtime_minutes, description
            )

            # Calculate Daily Salary
            daily_salary = self.daily_salary_repo.get_by_employee_id(payload.employee_id)
            if daily_salary:
                hours_worked = Decimal(
                    (updated_attendance.check_out - updated_attendance.check_in).total_seconds() / 3600
                ).quantize(Decimal('0.01'))
                # hours_worked = Decimal(7)

                # Normal salary calculation
                normal_salary = Decimal(daily_salary.standard_hours) * Decimal(daily_salary.hours_rate)

                # Overtime calculation
                overtime_pay = Decimal(0)
                if overtime_minutes > daily_salary.min_overtime:  # Min overtime in minutes
                    overtime_pay = Decimal(overtime_hours) * Decimal(daily_salary.overtime_rate)

                # Late deduction calculation
                late_deduction = Decimal(0)
                if late_minutes > daily_salary.max_late:  # Deduction applies only if late exceeds max_late
                    excess_late_minutes = late_minutes - daily_salary.max_late  # Calculate excess late minutes
                    excess_late_hours = Decimal(excess_late_minutes) // Decimal(60)  # Hours
                    remaining_late_minutes = Decimal(excess_late_minutes) % Decimal(60)  # Remaining minutes
                    total_excess_hours = excess_late_hours + (
                                remaining_late_minutes / Decimal(60))  # Total excess hours
                    late_deduction = (total_excess_hours * Decimal(daily_salary.late_deduction_rate)).quantize(
                        Decimal('0.01'), rounding=ROUND_DOWN
                    )

                logger.info(f"Late minutes: {late_minutes}")
                logger.info(
                    f"Excess late minutes: {excess_late_minutes if late_minutes > daily_salary.max_late else 0}")
                logger.info(f"Excess late hours: {total_excess_hours if late_minutes > daily_salary.max_late else 0}")
                logger.info(f"Late deduction: {late_deduction}")

                # Adjusted salary
                adjusted_salary = (hours_worked * Decimal(daily_salary.hours_rate)).quantize(Decimal('0.01'))

                # Total salary calculation
                total_salary = (adjusted_salary + overtime_pay - late_deduction).quantize(Decimal('0.01'))

                # Logging for debugging
                logger.info(f"Hours worked: {hours_worked}")
                logger.info(f"Normal salary: {normal_salary}")
                logger.info(f"Overtime pay: {overtime_pay}")
                logger.info(f"Late deduction: {late_deduction}")
                logger.info(f"Adjusted salary: {adjusted_salary}")
                logger.info(f"Total salary: {total_salary}")

                # Payload untuk gaji harian
                new_salary_payload = CreateNewEmployeeDailySalary(
                    employee_id=payload.employee_id,
                    work_date=today_start.date(),
                    hours_worked=Decimal(hours_worked),
                    late_deduction=Decimal(late_deduction),
                    overtime_pay=Decimal(overtime_pay),
                    month=today_start.month,
                    year=today_start.year,
                    normal_salary=Decimal(normal_salary),
                    total_salary=Decimal(total_salary),
                )
                logger.info(f"New salary payload: {new_salary_payload}")

                # Periksa apakah data gaji sudah ada
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

    def create(self, payload: IdentifyEmployee) -> Tuple[Attendance, dict]:
        if not payload.image:
            raise HTTPException(status_code=400, detail="Image is required")

        logger.info("Starting face identification process")

        # Process the input image
        try:
            input_image = self.process_base64_image(payload.image)
            input_encoding = self.get_face_encoding(input_image)
            logger.info("Successfully processed input image and got face encoding")
        except Exception as e:
            logger.error(f"Error processing input image: {str(e)}")
            raise HTTPException(status_code=400, detail=f"Error processing input image: {str(e)}")

        # Retrieve all employees from the database for comparison
        employees = self.face_repo.get_all_faces_with_employees()
        if not employees:
            logger.warning("No employees found in database")
            raise HTTPException(status_code=404, detail="No employees found in database")

        logger.info(f"Found {len(employees)} employees in database")

        best_match = None
        min_distance = 1.0

        for i, employee in enumerate(employees):
            logger.info(f"Processing employee {i + 1}/{len(employees)}")

            employee_data = self.row_to_dict(employee)
            face_image = employee_data.get('photo') or employee_data.get('image_base64')

            if not face_image:
                logger.warning(f"No face image found for employee {employee_data.get('employee_id', 'unknown')}")
                continue

            try:
                employee_img_array = self.process_base64_image(face_image)
                employee_encoding = self.get_face_encoding(employee_img_array)

                distance = face_recognition.face_distance([employee_encoding], input_encoding)[0]
                logger.info(f"Face distance for employee {i + 1}: {distance}")

                if distance < min_distance and distance < 0.5:
                    min_distance = distance
                    best_match = employee_data
                    logger.info(f"New best match found with distance: {distance}")
            except Exception as e:
                logger.warning(f"Error processing employee image: {str(e)}")
                continue

        if best_match:
            logger.info(f"Best match found with distance: {min_distance}")

            employee_id = best_match.get('employee_id')
            user_name = best_match.get('user_name', 'Unknown')
            company_id = best_match.get('company_id')
            company_name = self.company_repo.get_company_name_by_id(company_id)

            if not employee_id:
                logger.error("Invalid employee data: missing employee_id")
                raise HTTPException(
                    status_code=500,
                    detail="Invalid employee data: missing employee_id"
                )

            # Check for existing attendance for today
            today_start = datetime.now(jakarta_timezone).replace(hour=0, minute=0, second=0, microsecond=0)
            existing_attendance = self.attendance_repo.existing_attendance(employee_id, today_start)

            if existing_attendance:
                # Perform check-out if there is an existing attendance
                check_out_time = datetime.now(jakarta_timezone)
                update_payload = UpdateCheckOut(
                    company_id=company_id,
                    employee_id=employee_id,
                    check_out=check_out_time,
                    photo_out=payload.image,
                    location=payload.location
                )
                updated_attendance = self.update_check_out(update_payload)
                action = "Check-out"
            else:
                # Perform check-in if no existing attendance
                check_in_time = datetime.now(jakarta_timezone)
                check_in_payload = CreateCheckIn(
                    company_id=company_id,
                    employee_id=employee_id,
                    check_in=check_in_time,
                    photo_in=payload.image,
                    location=payload.location
                )
                updated_attendance = self.create_check_in(check_in_payload)
                action = "Check-in"

            employee_response = {
                'id': employee_id,
                'user_name': user_name,
                'nik': best_match.get('nik', ''),
                'email': best_match.get('email', ''),
                'company_id': company_id,
                'company_name': company_name,
                'action': action
            }

            logger.info(f"Successfully performed {action} for employee.")
            return updated_attendance, employee_response

        logger.warning("No matching face found")
        raise HTTPException(status_code=404, detail="No matching face found")

    def identify_face_employee(self, payload: IdentifyEmployee, user_company_id: uuid.UUID) -> Tuple[Attendance, dict]:
        if user_company_id is None:
            raise UnprocessableException("Company ID is required but not provided.")

        try:
            # Retrieve the company to verify it exists and is accessible
            company = self.company_repo.get_company_by_id(user_company_id)
            if not company:
                raise UnprocessableException("Company not found.")

            # Perform face identification via RisetAI
            trx_id = uuid.uuid4()
            identify = IdentifyFace(
                facegallery_id=str(company.id),
                image=payload.image,
                trx_id=str(trx_id)
            )

            # Call the face API client to identify the face
            url, data = self.face_api_clients.identify_face_employee(identify)
            user_id = data[0].get("user_id")

            # Check if the identified user ID matches an existing employee
            check_employee = self.employee_repo.is_nik_used(user_id)
            if not check_employee:
                raise UnprocessableException("VISITOR NOT VALID")

            employee = self.employee_repo.get_employee_bynik(user_id)

            # Check for existing attendance for today
            today_start = datetime.now(jakarta_timezone).replace(hour=0, minute=0, second=0, microsecond=0)
            existing_attendance = self.attendance_repo.existing_attendance(employee.id, today_start)

            if existing_attendance:
                # Perform check-out if there is an existing attendance
                check_out_time = datetime.now(jakarta_timezone)
                update_payload = UpdateCheckOut(
                    company_id=company.id,
                    employee_id=employee.id,
                    check_out=check_out_time,
                    photo_out=payload.image,
                    location=payload.location
                )
                updated_attendance = self.update_check_out(update_payload)
                action = "Check-out"
            else:
                # Perform check-in if no existing attendance
                check_in_time = datetime.now(jakarta_timezone)
                check_in_payload = CreateCheckIn(
                    company_id=company.id,
                    employee_id=employee.id,
                    check_in=check_in_time,
                    photo_in=payload.image,
                    location=payload.location
                )
                updated_attendance = self.create_check_in(check_in_payload)
                action = "Check-in"

            # Prepare employee response data
            employee_response = {
                'id': employee.id,
                'user_name': employee.user_name,
                'nik': employee.nik,
                'company_id': company.id,
                'company_name': company.name,
                'action': action
            }

            logger.info(f"Successfully performed {action} for employee via RisetAI.")
            return updated_attendance, employee_response

        except Exception as err:
            err_msg = str(err)
            logger.error(f"Error in identify_face_employee: {err_msg}")
            raise InternalErrorException(err_msg)


