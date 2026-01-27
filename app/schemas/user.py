from uuid import UUID
from pydantic import BaseModel, EmailStr

class UserOut(BaseModel):
    id: UUID
    email: EmailStr
    role: str
    is_active: bool

    class Config:
        from_attributes = True


class PasswordUpdateIn(BaseModel):
    new_password: str
    confirm_password: str
