from typing import List, Tuple
import uuid

from app.clients.face_api import FaceApiClient
from app.models.company import Company
from app.repositories.company import CompanyRepository
from app.schemas.company import CompanyFilter, CreateNewCompany, UpdateCompany, CompanyData, CreateFaceGalleryCompany
from app.schemas.faceapi_mgt import CreateFaceGallery, DeleteFaceGallery
from app.utils.exception import UnprocessableException, InternalErrorException
from app.utils.logger import logger

class CompanyService:
    def __init__(self) -> None:
        self.clients = FaceApiClient()
        self.company_repo = CompanyRepository()

    def create_company(self, payload: CreateNewCompany) -> CompanyData:
        try:
            # Membuat perusahaan
            company = self.company_repo.insert(payload)

            # Setelah membuat perusahaan, buat FaceGallery dengan ID perusahaan
            payload_facegallery = CreateFaceGallery(facegallery_id=str(company.id), trx_id=str(company.id))
            facegallery = self.clients.create_facegallery(payload_facegallery)

            if facegallery is None:
                raise InternalErrorException("Failed to create FaceGallery.")

        except Exception as err:
            err_msg = str(err)
            logger.error(err_msg)
            raise InternalErrorException(err_msg)

        return company

    def get_company(self, company_id: uuid.UUID) -> CompanyData:
        company = self.company_repo.get_company_by_id(company_id)
        if company is None:
            raise UnprocessableException("Company not found")
        return company

    def list_companies(self, filter: CompanyFilter) -> Tuple[List[CompanyData], int, int]:
        companies = self.company_repo.get_all_filtered(filter)
        total_rows = self.company_repo.count_by_filter(filter)
        total_pages = (total_rows + filter.limit - 1) // filter.limit if filter.limit else 1
        return companies, total_rows, total_pages

    def update_company(self, company_id: uuid.UUID, payload: UpdateCompany) -> CompanyData:
        company = self.company_repo.update(company_id, payload)
        if company is None:
            raise UnprocessableException("Company not found or could not be updated")
        return company

    def delete_company(self, company_id: uuid.UUID) -> CompanyData:
        try:
            # Menghapus perusahaan (soft delete)
            company = self.company_repo.delete_company_by_id(company_id)
            if company is None:
                raise UnprocessableException("Company not found")

            # Hapus FaceGallery menggunakan ID yang sama
            payload_facegallery = DeleteFaceGallery(facegallery_id=str(company_id), trx_id=str(company_id))
            delete_response = self.clients.delete_facegallery(payload_facegallery)

            if delete_response is None:
                raise InternalErrorException("Failed to delete FaceGallery.")

        except Exception as err:
            err_msg = str(err)
            logger.error(err_msg)
            raise InternalErrorException(err_msg)

        return company

    def insert_facegallery(self, company_id: uuid.UUID) -> Company:
        # Periksa apakah company_id sudah ada di database
        # is_company_exist = self.company_repo.is_company_exist(company_id)
        # if is_company_exist:
        #     raise UnprocessableException("Company already exists")

        try:
            client = self.company_repo.insertFaceGallery(company_id)
            if client:
                payload = CreateFaceGallery(facegallery_id=str(company_id), trx_id=str(client.id))
                facegallery = self.clients.create_facegallery(payload)
        except Exception as err:
            err_msg = str(err)
            logger.error(err_msg)
            raise InternalErrorException(err_msg)

        return facegallery

