import base64
import requests
from fastapi import status
from app.core.config import settings
from app.clients.email.schema import MailgunMessage
from app.utils.logger import logger


class MailgunClient:
    def __init__(self) -> None:
        self.base_url = settings.mailgun_url
        self.key = settings.mailgun_key
        self.domain = settings.mailgun_domain
        self.email = settings.mailgun_from
        credentials = f"api:{self.key}"
        encoded_credentials = base64.b64encode(credentials.encode("utf-8")).decode(
            "utf-8"
        )
        auth_header = f"Basic {encoded_credentials}"
        self.headers = {
            "Authorization": auth_header,
        }

    def send_text(
            self, email: str, text: str, subject: str = None
    ) -> MailgunMessage | None:
        url = f"{self.base_url}/v3/{self.domain}/messages"
        if subject is None:
            subject = "Notification"

        payload = {
            "from": self.email,
            "to": email,
            "subject": subject,
            "text": text,
        }

        try:
            response = requests.request("POST", url, headers=self.headers, data=payload)

            # Log full response details for debugging
            logger.info(f"Mailgun Response Status: {response.status_code}")
            logger.info(f"Mailgun Response Headers: {response.headers}")
            logger.info(f"Mailgun Response Content: {response.text}")

            if response.status_code == status.HTTP_200_OK:
                return MailgunMessage.parse_obj(response.json())

            # More detailed error logging
            logger.error(f"MAIL Send Failed - Status {response.status_code}")
            logger.error(f"Response Content: {response.text}")

            return None

        except Exception as e:
            logger.error(f"Exception in sending email: {str(e)}")
            return None

    def send_admin_text(self, text: str, subject: str = None) -> MailgunMessage | None:
        email = settings.notif_email
        return self.send_text(email, text, subject)