import base64
from math import ceil
from typing import List, Optional, Tuple
import uuid

from app.clients.face_api import FaceApiClient
from app.repositories.face import FaceRepository
from app.repositories.company import CompanyRepository
from app.repositories.employee import EmployeeRepository
from app.schemas.face_mgt import CreateFace, UpdateFace, FaceData
from app.schemas.faceapi_mgt import CreateEnrollFace
from app.utils.exception import UnprocessableException, InternalErrorException
from app.utils.logger import logger


class FaceService:
    def __init__(self) -> None:
        self.face_api_clients = FaceApiClient()
        self.face_repo = FaceRepository()
        self.company_repo = CompanyRepository()
        self.employee_repo = EmployeeRepository()

    def encode_image(self, path_image: str):
        file_content = path_image.file.read()
        with open(path_image.filename, "wb") as f:
            encoded_string = base64.b64encode(file_content)

        return encoded_string

    def list_faces(self, company_id: Optional[uuid.UUID], limit: int, page: int) -> Tuple[List[FaceData], int, int]:
        """
        Retrieve paginated list of faces for a specific company if provided.
        Returns faces, total_records, and total_pages.
        """
        total_records = self.face_repo.count_faces(company_id)
        total_pages = ceil(total_records / limit) if total_records > 0 else 1
        offset = (page - 1) * limit

        faces = self.face_repo.get_all_faces(company_id, limit, offset)
        return faces, total_records, total_pages

    def get_face(self, face_id: uuid.UUID) -> FaceData:
        """
        Retrieve a single face by its ID.
        """
        face = self.face_repo.get_by_id(face_id)
        if not face:
            raise UnprocessableException("Face not found.")
        return face

    def create_face(self, payload: CreateFace) -> Tuple[FaceData, str]:
        # Validate company_id
        company = self.company_repo.get_company_by_id(payload.company_id)
        if not company:
            raise UnprocessableException(f"Company with ID {payload.company_id} not found.")

        # Validate employee_id
        employee = self.employee_repo.get_employee_by_id(payload.employee_id)
        if not employee:
            raise UnprocessableException(f"Employee with ID {payload.employee_id} not found.")

        try:
            # Create face entry in the repository
            face = self.face_repo.create_face(payload)

            # Generate a unique transaction ID
            trx_id = uuid.uuid4()

            # Prepare enroll data for the face API
            enroll = CreateEnrollFace(
                user_id=str(employee.nik),
                user_name=employee.user_name,
                facegallery_id=str(company.id),
                image=payload.photo,
                trx_id=str(trx_id)
            )

            # Call face API to enroll the face and get the URL response
            face_api_response, _ = self.face_api_clients.insert_faces_visitor(enroll)

        except Exception as err:
            logger.error(f"Error during face enrollment: {err}")
            raise InternalErrorException("Failed to enroll face.")

        return face, face_api_response

    def update_face(self, face_id: uuid.UUID, payload: UpdateFace) -> FaceData:
        # Validasi company_id jika diberikan pada payload
        if payload.company_id:
            company = self.company_repo.get_company_by_id(payload.company_id)
            if not company:
                raise UnprocessableException(f"Company with ID {payload.company_id} not found.")

        # Validasi employee_id jika diberikan pada payload
        if payload.employee_id:
            employee = self.employee_repo.get_employee_by_id(payload.employee_id)
            if not employee:
                raise UnprocessableException(f"Employee with ID {payload.employee_id} not found.")

        # Melanjutkan proses update setelah validasi
        face = self.face_repo.update_face(face_id, payload)
        if not face:
            raise UnprocessableException("Face not found or could not be updated.")
        return face

    def delete_face(self, face_id: uuid.UUID) -> FaceData:
        face = self.face_repo.delete_face(face_id)
        if not face:
            raise UnprocessableException("Face not found.")
        return face
