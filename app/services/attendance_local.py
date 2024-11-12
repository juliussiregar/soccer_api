# from typing import List, Tuple, Type, Optional, Dict, Any
# from fastapi import HTTPException
# from datetime import date, datetime
# import pytz
# import numpy as np
# import face_recognition
# import base64
# from io import BytesIO
# from PIL import Image
# from sqlalchemy.engine.row import Row

# from app.models.attendance_local import AttendanceLocal
# from app.repositories.attendance_local import AttendanceLocalRepository
# from app.repositories.face import FaceRepository
# from app.repositories.visitor import VisitorRepository
# from app.schemas.faceapi_mgt import IdentifyFaceLocal
# from app.services.visitor import VisitorService
# from app.schemas.visitor import IdentifyVisitor
# from app.schemas.attendance_local_mgt import CreateCheckIn
# from app.models.employee import Visitor
# from app.utils.exception import InternalErrorException, UnprocessableException
# from app.utils.logger import logger


# def process_base64_image(base64_string: str) -> np.ndarray:
#     """Convert base64 string to numpy array in RGB format."""
#     try:
#         # Remove potential data URI prefix
#         if 'base64,' in base64_string:
#             base64_string = base64_string.split('base64,')[1]

#         img_data = base64.b64decode(base64_string)
#         img = Image.open(BytesIO(img_data))
#         # Convert directly to RGB format
#         img = img.convert('RGB')
#         # Convert to numpy array
#         return np.array(img)
#     except Exception as e:
#         logger.error(f"Error processing base64 image: {str(e)}")
#         raise HTTPException(status_code=400, detail=f"Invalid image format: {str(e)}")


# def get_start_of_day(dt: datetime) -> datetime:
#     """Helper function to get the start of the current day."""
#     return dt.replace(hour=0, minute=0, second=0, microsecond=0)


# def get_face_encoding(img_array: np.ndarray) -> np.ndarray:
#     """Generate face encoding from an RGB image array."""
#     face_locations = face_recognition.face_locations(img_array)

#     if not face_locations:
#         raise HTTPException(status_code=400, detail="No face detected in the image")

#     return face_recognition.face_encodings(img_array, face_locations)[0]


# def row_to_dict(row: Row) -> dict:
#     """Convert SQLAlchemy Row to dictionary."""
#     try:
#         return {key: getattr(row, key) for key in row._fields}
#     except Exception as e:
#         logger.error(f"Error converting row to dict: {str(e)}")
#         return {}


# class AttendanceLocalService:
#     def __init__(self) -> None:
#         self.visitor_service = VisitorService()
#         self.attendance_local_repo = AttendanceLocalRepository()
#         self.face_repo = FaceRepository()

#     def list(self, filter_date: date) -> list[AttendanceLocal]:
#         visitors_today = self.attendance_local_repo.get_all_filtered(filter_date)
#         return visitors_today

#     def create(self, payload: IdentifyVisitor) -> Tuple[CreateCheckIn, dict]:
#         if not payload.image:
#             raise HTTPException(status_code=400, detail="Image is required")

#         logger.info("Starting face identification process")

#         # Process the input image
#         try:
#             input_image = process_base64_image(payload.image)
#             input_encoding = get_face_encoding(input_image)
#             logger.info("Successfully processed input image and got face encoding")
#         except Exception as e:
#             logger.error(f"Error processing input image: {str(e)}")
#             raise HTTPException(status_code=400, detail=f"Error processing input image: {str(e)}")

#         # Retrieve all visitors from the database for comparison
#         visitors = self.face_repo.get_all_faces_with_visitors()
#         if not visitors:
#             logger.warning("No visitors found in database")
#             raise HTTPException(status_code=404, detail="No visitors found in database")

#         logger.info(f"Found {len(visitors)} visitors in database")

#         best_match = None
#         min_distance = 1.0

#         for i, visitor in enumerate(visitors):
#             logger.info(f"Processing visitor {i + 1}/{len(visitors)}")

#             visitor_data = row_to_dict(visitor)
#             face_image = visitor_data.get('face_image') or visitor_data.get('image_base64')

#             if not face_image:
#                 logger.warning(f"No face image found for visitor {visitor_data.get('visitor_id', 'unknown')}")
#                 continue

#             try:
#                 visitor_img_array = process_base64_image(face_image)
#                 visitor_encoding = get_face_encoding(visitor_img_array)

#                 distance = face_recognition.face_distance([visitor_encoding], input_encoding)[0]
#                 logger.info(f"Face distance for visitor {i + 1}: {distance}")

#                 if distance < min_distance and distance < 0.5:
#                     min_distance = distance
#                     best_match = visitor_data
#                     logger.info(f"New best match found with distance: {distance}")
#             except Exception as e:
#                 logger.warning(f"Error processing visitor image: {str(e)}")
#                 continue

#         if best_match:
#             logger.info(f"Best match found with distance: {min_distance}")

#             visitor_id = best_match.get('visitor_id')
#             full_name = best_match.get('full_name', 'Unknown')

#             if not visitor_id:
#                 logger.error("Invalid visitor data: missing visitor_id")
#                 raise HTTPException(
#                     status_code=500,
#                     detail="Invalid visitor data: missing visitor_id"
#                 )

#             today_start = get_start_of_day(datetime.now(pytz.timezone('Asia/Jakarta')))

#             existing_attendance = self.attendance_local_repo.existing_attendance(
#                 visitor_id=visitor_id,
#                 full_name=full_name,
#                 today_start=today_start
#             )

#             try:
#                 check_in_time = datetime.now(pytz.timezone('Asia/Jakarta'))
#                 new_attendance = CreateCheckIn(
#                     visitor_id=visitor_id,
#                     full_name=full_name,
#                     check_in=check_in_time
#                 )
#                 self.attendance_local_repo.insert_attendance_checkin(new_attendance)

#                 visitor_response = {
#                     'id': visitor_id,
#                     'full_name': full_name,
#                     'nik': best_match.get('nik', ''),
#                     'company': best_match.get('company', ''),
#                     'address': best_match.get('address', '')
#                 }

#                 logger.info("Successfully created attendance record")
#                 return new_attendance, visitor_response

#             except Exception as e:
#                 logger.error(f"Error recording attendance: {str(e)}")
#                 raise HTTPException(status_code=500, detail=f"Error recording attendance: {str(e)}")

#         logger.warning("No matching face found")
#         raise HTTPException(status_code=404, detail="No matching face found")