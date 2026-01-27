from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.deps import get_db
from app.core.security import create_access_token
from app.schemas.auth import ForgotPasswordIn, LoginIn, MessageOut, ResetPasswordIn, TokenOut
from app.services import auth_service, email_service
from app.core.security import verify_password_reset_token
from app.repositories import user_repo

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenOut)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
) -> TokenOut:
    user = auth_service.authenticate_user(db, form_data.username, form_data.password)
    token = create_access_token(str(user.id), user.role)
    return TokenOut(access_token=token)


@router.post("/login-json", response_model=TokenOut)
async def login_json(payload: LoginIn, db: Session = Depends(get_db)) -> TokenOut:
    user = auth_service.authenticate_user(db, payload.email, payload.password)
    token = create_access_token(str(user.id), user.role)
    return TokenOut(access_token=token)


@router.post("/forgot-password", response_model=MessageOut)
async def forgot_password(payload: ForgotPasswordIn, db: Session = Depends(get_db)) -> MessageOut:
    result = auth_service.request_password_reset(db, payload.email)
    if not result:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="Email not found")

    user, token = result
    reset_link = f"{settings.FRONTEND_URL}/admin/reset-password?token={token}"
    subject, text_body, html_body = email_service.build_reset_password_email(
        admin_name="Admin",
        email=user.email,
        reset_link=reset_link,
    )
    await email_service.send_email(
        db,
        user.email,
        subject,
        text_body,
        html_body=html_body,
    )
    return MessageOut(message="Reset link sent.")


@router.post("/reset-password", response_model=MessageOut)
async def reset_password(payload: ResetPasswordIn, db: Session = Depends(get_db)) -> MessageOut:
    auth_service.reset_password(db, payload.token, payload.new_password)
    return MessageOut(message="Password reset successful.")


@router.get("/verify-reset-token", response_model=MessageOut)
async def verify_reset_token(token: str, db: Session = Depends(get_db)) -> MessageOut:
    try:
        user_id = UUID(verify_password_reset_token(token))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    user = user_repo.get_by_id(db, user_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=404, detail="User not found or inactive")
    return MessageOut(message="Token is valid.")
