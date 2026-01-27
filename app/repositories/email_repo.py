from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.db.models.email_log import EmailLog


def create_log(db: Session, to_email: str, subject: str, body: str) -> EmailLog:
    log = EmailLog(to_email=to_email, subject=subject, body=body, status="QUEUED")
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


def update_log(db: Session, log: EmailLog, status: str, error_message: str | None = None) -> EmailLog:
    log.status = status
    log.error_message = error_message
    if status == "SENT":
        log.sent_at = datetime.now(timezone.utc)
    db.add(log)
    db.commit()
    db.refresh(log)
    return log
