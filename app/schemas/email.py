from pydantic import BaseModel, EmailStr

class EmailSendIn(BaseModel):
    to_email: EmailStr
    subject: str
    body: str
