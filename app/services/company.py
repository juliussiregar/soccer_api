from typing import List, Tuple
import uuid
from app.repositories.company import CompanyRepository
from app.schemas.company import CompanyFilter, CreateNewCompany, UpdateCompany, CompanyData
from app.utils.exception import UnprocessableException, InternalErrorException
from app.utils.logger import logger

class CompanyService:
    def __init__(self) -> None:
        self.company_repo = CompanyRepository()

    def create_company(self, payload: CreateNewCompany) -> CompanyData:
        try:
            company = self.company_repo.insert(payload)
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
        company = self.company_repo.delete_company_by_id(company_id)
        if company is None:
            raise UnprocessableException("Company not found")
        return company
