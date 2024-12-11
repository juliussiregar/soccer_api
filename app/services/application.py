# services/application.py

from typing import List, Tuple
import uuid

from app.clients.email.email import MailgunClient
from app.repositories.application import ApplicationRepository
from app.schemas.application import ApplicationFilter, CreateNewApplication, UpdateApplication, ApplicationData
from app.utils.exception import UnprocessableException, InternalErrorException
from app.utils.logger import logger


class ApplicationService:
    def __init__(self):
        self.mailgun_client = MailgunClient()
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

    def update_application(self, application_id: int, payload: UpdateApplication, generate_token: str) -> ApplicationData:
        try:
            find_application_id = self.application_repo.get_application_by_id(application_id)

            # First, get the employee's email before updating
            email = self.application_repo.get_email_by_employee_id(find_application_id.employee_id)

            # Prepare email content based on the new status
            if payload.status == "Accepted":
                email_subject = "Application Accepted"
                email_text = (
                    "Congratulations! Your application has been accepted.\n\n"
                    "Please use the following link to access your attendance system and set up your check-in/check-out:\n"
                    f"http://localhost:3000/wfh-check-in-out?token={generate_token}"
                )
            elif payload.status == "Rejected":
                email_subject = "Application Rejected"
                email_text = "We regret to inform you that your application has been rejected."
            else:
                email_text = None

            # Send email if status is changing to Accepted or Rejected
            if email_text and email:
                email_result = self.mailgun_client.send_text(
                    email=email,
                    text=email_text,
                    subject=email_subject
                )

                # If email sending fails, raise an exception to prevent application update
                if email_result is None:
                    logger.error(f"Failed to send email to {email} for application {application_id}")
                    raise InternalErrorException("Failed to send notification email")

            # Update the application
            application = self.application_repo.update(application_id, payload)

            if application is None:
                raise UnprocessableException("Application not found or could not be updated")

            return application

        except Exception as e:
            logger.error(f"Error in update_application: {str(e)}")
            raise

    def delete_application(self, application_id: int) -> ApplicationData:
        application = self.application_repo.delete_application_by_id(application_id)
        if application is None:
            raise UnprocessableException("Application not found")
        return application
