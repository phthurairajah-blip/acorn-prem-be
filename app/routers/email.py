from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_db, require_role
from app.schemas.auth import MessageOut
from app.schemas.email import EmailSendIn
from app.services import email_service

router = APIRouter(prefix="/email", tags=["email"])


@router.post("/send", response_model=MessageOut)
async def send_email(
    payload: EmailSendIn,
    db: Session = Depends(get_db),
    _: object = Depends(require_role("ADMIN")),
) -> MessageOut:
    await email_service.send_email(db, payload.to_email, payload.subject, payload.body)
    return MessageOut(message="Email sent.")
