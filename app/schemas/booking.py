from datetime import date, datetime
from uuid import UUID
from pydantic import BaseModel, EmailStr


class BookingCreate(BaseModel):
    name: str
    email: EmailStr
    phone: str | None = None
    preferred_date: date | None = None
    preferred_time: str | None = None
    preferred_location: str | None = None
    message: str | None = None
    recaptcha_token: str


class BookingOut(BaseModel):
    id: UUID
    name: str
    email: EmailStr
    phone: str | None = None
    preferred_date: date | None = None
    preferred_time: str | None = None
    preferred_location: str | None = None
    message: str | None = None
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
