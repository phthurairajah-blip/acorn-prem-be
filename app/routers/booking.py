from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.core.deps import get_db, require_role
from app.db.models.user import User
from app.schemas.auth import MessageOut
from app.schemas.booking import BookingCreate, BookingOut
from app.services import booking_service

router = APIRouter(prefix="/bookings", tags=["bookings"])


@router.get("/", response_model=list[BookingOut])
def list_bookings(
    db: Session = Depends(get_db),
    _: User = Depends(require_role("ADMIN")),
) -> list[BookingOut]:
    return booking_service.list_bookings(db)


@router.get("/{booking_id}", response_model=BookingOut)
def get_booking(
    booking_id: UUID,
    db: Session = Depends(get_db),
    _: User = Depends(require_role("ADMIN")),
) -> BookingOut:
    booking = booking_service.get_booking(db, booking_id)
    if not booking:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")
    return booking


@router.post("/", response_model=MessageOut)
async def create_booking(
    payload: BookingCreate,
    request: Request,
    db: Session = Depends(get_db),
) -> MessageOut:
    await booking_service.create_booking(db, payload, request.client.host if request.client else None)
    return MessageOut(message="Booking request received.")


@router.delete("/{booking_id}", response_model=MessageOut)
def delete_booking(
    booking_id: UUID,
    db: Session = Depends(get_db),
    _: User = Depends(require_role("ADMIN")),
) -> MessageOut:
    booking = booking_service.get_booking(db, booking_id)
    if not booking:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")
    booking_service.delete_booking(db, booking)
    return MessageOut(message="Booking deleted.")
