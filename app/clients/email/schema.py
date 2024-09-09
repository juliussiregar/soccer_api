from pydantic import BaseModel


class MailgunMessage(BaseModel):
    id: str
    message: str
