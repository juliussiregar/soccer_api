# services/application.py

from typing import List, Tuple
import uuid
from app.repositories.application import ApplicationRepository
from app.schemas.application import ApplicationFilter, CreateNewApplication, UpdateApplication, ApplicationData
from app.utils.exception import UnprocessableException, InternalErrorException

class ApplicationService:
    def __init__(self):
        self.application_repo = ApplicationRepository()

    def create_application(self, payload: CreateNewApplication) -> ApplicationData:
        try:
            application = self.application_repo.insert(payload)
        except Exception as e:
            raise InternalErrorException(str(e))
        return application

    def get_application(self, application_id: int) -> ApplicationData:
        application = self.application_repo.get_application_by_id(application_id)
        if application is None:
            raise UnprocessableException("Application not found")
        return application

    def list_applications(self, filter: ApplicationFilter) -> Tuple[List[ApplicationData], int, int]:
        applications = self.application_repo.get_all_filtered(filter)
        total_rows = self.application_repo.count_by_filter(filter)
        total_pages = (total_rows + filter.limit - 1) // filter.limit if filter.limit else 1
        return applications, total_rows, total_pages
    
    def update_application(self, application_id: int, payload: UpdateApplication) -> ApplicationData:
        application = self.application_repo.update(application_id, payload)
        if application is None:
            raise UnprocessableException("Application not found or could not be updated")
        return application

    def delete_application(self, application_id: int) -> ApplicationData:
        application = self.application_repo.delete_application_by_id(application_id)
        if application is None:
            raise UnprocessableException("Application not found")
        return application
