from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import (
    create_password_reset_token,
    hash_password,
    verify_password,
    verify_password_reset_token,
)
from app.db.models.user import User
from app.repositories import user_repo


def authenticate_user(db: Session, email: str, password: str) -> User:
    user = user_repo.get_by_email(db, email)
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is inactive")
    return user


def ensure_default_admin(db: Session) -> User | None:
    if not settings.ADMIN_SEED_EMAIL or not settings.ADMIN_SEED_PASSWORD:
        return None
    user = user_repo.get_by_email(db, settings.ADMIN_SEED_EMAIL)
    if user:
        return user
    password_hash = hash_password(settings.ADMIN_SEED_PASSWORD)
    return user_repo.create_user(
        db,
        settings.ADMIN_SEED_EMAIL,
        password_hash,
        role=settings.ADMIN_SEED_ROLE,
    )


def request_password_reset(db: Session, email: str) -> tuple[User, str] | None:
    user = user_repo.get_by_email(db, email)
    if not user or not user.is_active:
        return None
    token = create_password_reset_token(str(user.id))
    return user, token


def reset_password(db: Session, token: str, new_password: str) -> None:
    if len(new_password) < 8:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password must be at least 8 characters")
    try:
        user_id = UUID(verify_password_reset_token(token))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    user = user_repo.get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    user_repo.update_password(db, user, hash_password(new_password))
