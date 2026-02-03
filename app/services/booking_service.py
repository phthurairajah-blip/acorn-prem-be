from fastapi import HTTPException, status
from sqlalchemy.orm import Session
import httpx

from app.core.config import settings
from app.repositories import booking_repo
from app.schemas.booking import BookingCreate
from app.services import email_service


async def verify_recaptcha(token: str, remote_ip: str | None = None) -> None:
    if not settings.RECAPTCHA_SECRET:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Recaptcha not configured")
    payload = {
        "secret": settings.RECAPTCHA_SECRET,
        "response": token,
    }
    if remote_ip:
        payload["remoteip"] = remote_ip

    async with httpx.AsyncClient(timeout=10) as client:
        res = await client.post("https://www.google.com/recaptcha/api/siteverify", data=payload)
    data = res.json()
    if not data.get("success"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Recaptcha verification failed")


async def create_booking(db: Session, data: BookingCreate, remote_ip: str | None = None) -> None:
    await verify_recaptcha(data.recaptcha_token, remote_ip)
    booking = booking_repo.create(db, data)

    admin_email = settings.BOOKING_ADMIN_EMAIL
    if not admin_email:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Admin email not configured")
    cc_emails: list[str] | None = None
    if settings.BOOKING_ADMIN_EMAIL_CC:
        cc_emails = [
            email.strip()
            for email in settings.BOOKING_ADMIN_EMAIL_CC.split(",")
            if email.strip()
        ]

    subject, text_body, html_body = email_service.build_booking_email(
        name=booking.name,
        email=booking.email,
        phone=booking.phone,
        preferred_date=booking.preferred_date,
        preferred_time=booking.preferred_time,
        preferred_location=booking.preferred_location,
        message=booking.message,
    )
    await email_service.send_email(
        db,
        admin_email,
        subject,
        text_body,
        html_body=html_body,
        cc_emails=cc_emails,
    )


def list_bookings(db: Session, skip: int = 0, limit: int = 12):
    return booking_repo.list_bookings(db, skip=skip, limit=limit)


def get_booking(db: Session, booking_id):
    return booking_repo.get_by_id(db, booking_id)


def delete_booking(db: Session, booking):
    booking_repo.delete(db, booking)
