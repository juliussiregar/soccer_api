import base64
from io import BytesIO

import face_recognition
import numpy as np

from PIL import Image
from fastapi import HTTPException
from sqlalchemy import Row

from app.repositories.company import CompanyRepository
from app.repositories.face import FaceRepository
from app.repositories.attendance import AttendanceRepository
from app.schemas.attendance_mgt import IdentifyEmployee
from app.utils.logger import logger

class FaceRecognitionService:
    def __init__(self):
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
            return {
                'id': best_match.get('employee_id'),
                'user_name': best_match.get('user_name', 'Unknown'),
                'nik': best_match.get('nik', ''),
                'company_id': best_match.get('company_id'),
            }

        logger.warning("No matching face found")
        raise HTTPException(status_code=404, detail="No matching face found")