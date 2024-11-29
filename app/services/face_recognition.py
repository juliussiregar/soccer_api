from io import BytesIO

import pytz

from app.clients.face_api import FaceApiClient
from app.core.constants.app import DEFAULT_TZ
from app.repositories.daily_salary import DailySalaryRepository
from app.repositories.employee import EmployeeRepository
from app.repositories.employee_daily_salary import EmployeeDailySalaryRepository
from app.schemas.employee_daily_salary import CreateNewEmployeeDailySalary
from app.services.attendance import AttendanceService
from app.utils.calculate_salary import CalculateSalary
from app.utils.exception import InternalErrorException, UnprocessableException
from app.utils.logger import logger
import base64
from typing import Tuple
from datetime import datetime

import face_recognition
import numpy as np
import uuid

from PIL import Image
from fastapi import HTTPException
from sqlalchemy import Row

from app.models.attendance import Attendance
from app.repositories.company import CompanyRepository
from app.repositories.face import FaceRepository
from app.schemas.attendance_mgt import CreateCheckIn, UpdateCheckOut, IdentifyEmployee
from app.repositories.attendance import AttendanceRepository
from app.schemas.faceapi_mgt import IdentifyFace

# Define the default timezone
jakarta_timezone = pytz.timezone(DEFAULT_TZ)

class FaceRecognitionService:
    def __init__(self):
        self.calculate_salary_utils = CalculateSalary()

        self.face_api_clients = FaceApiClient()
        self.attendance_service = AttendanceService()

        self.employee_daily_salary_repo = EmployeeDailySalaryRepository()
        self.daily_salary_repo = DailySalaryRepository()
        self.employee_repo = EmployeeRepository()
        self.attendance_repo = AttendanceRepository()
        self.company_repo = CompanyRepository()
        self.face_repo = FaceRepository()

    def process_base64_image(self, base64_string: str) -> np.ndarray:
        """Convert base64 string to numpy array in RGB format."""
        try:
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

    def process_employees(self, employees: list, input_encoding: np.ndarray) -> dict:
        """Process employees to find the best match for the input encoding."""
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

        return best_match

    def detect_face(self, payload: IdentifyEmployee) -> dict:
        """Detect face and return matched employee details without creating attendance data."""
        if not payload.image:
            raise HTTPException(status_code=400, detail="Image is required")

        logger.info("Starting face detection process")

        try:
            input_image = self.process_base64_image(payload.image)
            input_encoding = self.get_face_encoding(input_image)
        except Exception as e:
            logger.error(f"Error processing input image: {str(e)}")
            raise HTTPException(status_code=400, detail=f"Error processing input image: {str(e)}")

        employees = self.face_repo.get_all_faces_with_employees()
        if not employees:
            logger.warning("No employees found in database")
            raise HTTPException(status_code=404, detail="No employees found in database")

        logger.info(f"Found {len(employees)} employees in database")
        best_match = self.process_employees(employees, input_encoding)

        if best_match:
            employee_id = best_match.get('employee_id')

            # Ambil data terakhir
            last_attendance = self.attendance_repo.get_last_attendance_by_employee_id(employee_id)

            # Default action adalah "Check-in"
            action = "Check-in"

            if last_attendance:
                if last_attendance.check_in and not last_attendance.check_out:
                    action = "Check-out"  # Jika sudah check-in tetapi belum check-out
                elif last_attendance.check_in and last_attendance.check_out:
                    action = "Check-in"  # Jika sudah check-in dan check-out

            return {
                'id': employee_id,
                'user_name': best_match.get('user_name', 'Unknown'),
                'nik': best_match.get('nik', ''),
                'company_id': best_match.get('company_id'),
                'action': action
            }

        logger.warning("No matching face found")
        raise HTTPException(status_code=404, detail="No matching face found")

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
                updated_attendance = self.attendance_service.update_check_out(update_payload)
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
                updated_attendance = self.attendance_service.create_check_in(check_in_payload)
                action = "Check-in"

            employee_response = {
                'id': employee_id,
                'user_name': user_name,
                'nik': best_match.get('nik', ''),
                'email': best_match.get('email', ''),
                'company_id': company_id,
                'company_name': company_name,
                'action': action,
                'timestamp': datetime.now(jakarta_timezone).strftime('%Y-%m-%d %H:%M:%S')
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
                raise UnprocessableException("EMPLOYEE NOT VALID")

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
                updated_attendance = self.attendance_service.update_check_out(update_payload)
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
                updated_attendance = self.attendance_service.create_check_in(check_in_payload)
                action = "Check-in"

            # Prepare employee response data
            employee_response = {
                'id': employee.id,
                'user_name': employee.user_name,
                'nik': employee.nik,
                'company_id': company.id,
                'company_name': company.name,
                'action': action,
                'timestamp': datetime.now(jakarta_timezone).strftime('%Y-%m-%d %H:%M:%S')
            }

            logger.info(f"Successfully performed {action} for employee via RisetAI.")
            return updated_attendance, employee_response

        except Exception as err:
            err_msg = str(err)
            logger.error(f"Error in identify_face_employee: {err_msg}")
            raise InternalErrorException(err_msg)

    def create_wfh(self, payload: IdentifyEmployee) -> Tuple[Attendance, dict]:
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
            company = self.company_repo.get_company_by_id(company_id)

            if not employee_id or not company:
                logger.error("Invalid employee or company data")
                raise HTTPException(status_code=500, detail="Invalid employee or company data")

            # Combine company start_time and end_time with today's date to get full datetime objects
            today_date = datetime.today().date()
            start_time = company.start_time
            end_time = company.end_time

            # Convert to datetime objects by combining with today's date
            check_in_time = datetime.combine(today_date, start_time)
            check_out_time = datetime.combine(today_date, end_time)

            # Prepare the comprehensive attendance payload
            check_in_payload = CreateCheckIn(
                company_id=company_id,
                employee_id=employee_id,
                check_in=check_in_time,
                photo_in=payload.image,
                location=payload.location,
                type="WFH"
            )

            # Create attendance record with check-in details
            updated_attendance = self.attendance_service.create_check_in(check_in_payload)

            # Immediately update check-out in the same record
            checkout_payload = UpdateCheckOut(
                company_id=company_id,
                employee_id=employee_id,
                check_out=check_out_time,
                photo_out=payload.image,
                location=payload.location
            )
            updated_attendance = self.attendance_service.update_check_out(checkout_payload)

            # Prepare employee response data
            employee_response = {
                'id': employee_id,
                'user_name': user_name,
                'nik': best_match.get('nik', ''),
                'email': best_match.get('email', ''),
                'company_id': company_id,
                'company_name': company_name,
                'action': "WFH Check-in and Check-out",
                'timestamp': datetime.now(jakarta_timezone).strftime('%Y-%m-%d %H:%M:%S')
            }

            logger.info("Successfully created WFH attendance record with check-in and check-out via Local method.")
            return updated_attendance, employee_response

        logger.warning("No matching face found")
        raise HTTPException(status_code=404, detail="No matching face found")

    def identify_face_employee_wfh(self, payload: IdentifyEmployee, user_company_id: uuid.UUID) -> Tuple[
        Attendance, dict]:
        if user_company_id is None:
            raise UnprocessableException("Company ID is required but not provided.")

        try:
            # Retrieve the company to verify it exists and is accessible
            company = self.company_repo.get_company_by_id(user_company_id)
            if not company:
                raise UnprocessableException("Company not found.")

            # Combine company start_time and end_time with today's date to get full datetime objects
            today_date = datetime.today().date()
            start_time = company.start_time
            end_time = company.end_time

            # Convert to datetime objects by combining with today's date
            check_in_time = datetime.combine(today_date, start_time)
            check_out_time = datetime.combine(today_date, end_time)

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
                raise UnprocessableException("EMPLOYEE NOT VALID")

            employee = self.employee_repo.get_employee_bynik(user_id)

            # Prepare the comprehensive attendance payload
            attendance_payload = CreateCheckIn(
                company_id=company.id,
                employee_id=employee.id,
                check_in=check_in_time,
                photo_in=payload.image,
                location=payload.location,
                type="WFH"  # Menambahkan tipe WFH
            )

            # Create attendance record with check-in details
            updated_attendance = self.attendance_service.create_check_in(attendance_payload)

            # Immediately update check-out in the same record
            checkout_payload = UpdateCheckOut(
                company_id=company.id,
                employee_id=employee.id,
                check_out=check_out_time,
                photo_out=payload.image,
                location=payload.location
            )
            updated_attendance = self.attendance_service.update_check_out(checkout_payload)

            # Prepare employee response data
            employee_response = {
                'id': employee.id,
                'user_name': employee.user_name,
                'nik': employee.nik,
                'company_id': company.id,
                'company_name': company.name,
                'action': "WFH Check-in and Check-out",
                'timestamp': datetime.now(jakarta_timezone).strftime('%Y-%m-%d %H:%M:%S')
            }

            logger.info("Successfully created WFH attendance record with check-in and check-out via RisetAI.")
            return updated_attendance, employee_response

        except Exception as err:
            err_msg = str(err)
            logger.error(f"Error in identify_face_employee_wfh: {err_msg}")
            raise InternalErrorException(err_msg)