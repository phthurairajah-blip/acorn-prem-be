from uuid import UUID
from sqlalchemy.orm import Session
from app.db.models.booking import Booking
from app.schemas.booking import BookingCreate


def create(db: Session, data: BookingCreate) -> Booking:
    booking = Booking(
        name=data.name.strip(),
        email=data.email,
        phone=data.phone,
        preferred_date=data.preferred_date,
        preferred_time=data.preferred_time,
        preferred_location=data.preferred_location,
        message=data.message,
    )
    db.add(booking)
    db.commit()
    db.refresh(booking)
    return booking


def list_bookings(db: Session, skip: int = 0, limit: int = 12) -> list[Booking]:
    return (
        db.query(Booking)
        .order_by(Booking.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_by_id(db: Session, booking_id: UUID) -> Booking | None:
    return db.get(Booking, booking_id)


def delete(db: Session, booking: Booking) -> None:
    db.delete(booking)
    db.commit()
