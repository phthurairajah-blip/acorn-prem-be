from fastapi_mail import ConnectionConfig, FastMail, MessageSchema
from sqlalchemy.orm import Session

from app.core.config import settings
from app.repositories import email_repo

conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_STARTTLS=settings.MAIL_STARTTLS,
    MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
)

mail_client = FastMail(conf)


async def send_email(
    db: Session,
    to_email: str,
    subject: str,
    body: str,
    html_body: str | None = None,
    cc_emails: list[str] | None = None,
) -> None:
    log = email_repo.create_log(db, to_email, subject, body)
    try:
        message_kwargs = {
            "subject": subject,
            "recipients": [to_email],
            "body": html_body if html_body else body,
            "subtype": "html" if html_body else "plain",
        }
        if cc_emails:
            message_kwargs["cc"] = cc_emails
        message = MessageSchema(**message_kwargs)
        await mail_client.send_message(message)
        email_repo.update_log(db, log, status="SENT")
    except Exception as exc:
        email_repo.update_log(db, log, status="FAILED", error_message=str(exc))
        raise


def build_reset_password_email(admin_name: str, email: str, reset_link: str) -> tuple[str, str, str]:
    subject = "Reset your password"
    text_body = (
        f"Hi {admin_name},\n\n"
        "We received a request to reset your password for your admin account.\n"
        f"Email: {email}\n\n"
        f"Reset your password using this link: {reset_link}\n\n"
        "If you did not request this, you can ignore this email.\n"
    )
    html_body = f"""\
<!doctype html>
<html>
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Reset your password</title>
  </head>
  <body style="margin:0;background:#f5f7fb;font-family:Arial,Helvetica,sans-serif;color:#0f172a;">
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#f5f7fb;padding:32px 0;">
      <tr>
        <td align="center">
          <table role="presentation" width="600" cellpadding="0" cellspacing="0" style="background:#ffffff;border-radius:16px;overflow:hidden;box-shadow:0 10px 30px rgba(15,23,42,0.08);">
            <tr>
              <td style="padding:28px 32px;background:#0f766e;color:#ffffff;">
                <div style="font-size:20px;font-weight:700;">Password Reset</div>
              </td>
            </tr>
            <tr>
              <td style="padding:32px;">
                <div style="font-size:18px;font-weight:600;margin-bottom:8px;">Hi {admin_name},</div>
                <div style="font-size:14px;line-height:1.6;color:#334155;">
                  We received a request to reset your password for your admin account.
                </div>
                <div style="margin:12px 0 20px 0;font-size:14px;color:#475569;">
                  Account email: <strong style="color:#0f172a;">{email}</strong>
                </div>
                <div>
                  <a href="{reset_link}" style="display:inline-block;background:#10b981;color:#ffffff;text-decoration:none;padding:12px 20px;border-radius:10px;font-weight:600;font-size:14px;">
                    Reset password
                  </a>
                </div>
                <div style="margin-top:16px;font-size:12px;color:#64748b;">
                  If the button doesn't work, copy and paste this link:
                  <div style="word-break:break-all;margin-top:6px;color:#0f172a;">{reset_link}</div>
                </div>
                <div style="margin-top:20px;font-size:12px;color:#94a3b8;">
                  If you did not request this, you can safely ignore this email.
                </div>
              </td>
            </tr>
            <tr>
              <td style="padding:20px 32px;background:#f8fafc;font-size:12px;color:#94a3b8;">
                This link will expire soon. Please reset your password promptly.
              </td>
            </tr>
          </table>
        </td>
      </tr>
    </table>
  </body>
</html>
"""
    return subject, text_body, html_body


def build_booking_email(
    name: str,
    email: str,
    phone: str | None,
    preferred_date,
    preferred_time: str | None,
    preferred_location: str | None,
    message: str | None,
) -> tuple[str, str, str]:
    subject = "New appointment request"
    date_text = preferred_date.isoformat() if preferred_date else "Flexible"
    time_text = preferred_time or "Flexible"
    location_text = preferred_location or "No preference"
    phone_text = phone or "Not provided"
    message_text = message or "None"

    text_body = (
        "New appointment request\n\n"
        f"Name: {name}\n"
        f"Email: {email}\n"
        f"Phone: {phone_text}\n"
        f"Preferred Date: {date_text}\n"
        f"Preferred Time: {time_text}\n"
        f"Preferred Location: {location_text}\n"
        f"Message: {message_text}\n"
    )

    html_body = f"""\
<!doctype html>
<html>
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>New appointment request</title>
  </head>
  <body style="margin:0;background:#f5f7fb;font-family:Arial,Helvetica,sans-serif;color:#0f172a;">
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#f5f7fb;padding:32px 0;">
      <tr>
        <td align="center">
          <table role="presentation" width="600" cellpadding="0" cellspacing="0" style="background:#ffffff;border-radius:16px;overflow:hidden;box-shadow:0 10px 30px rgba(15,23,42,0.08);">
            <tr>
              <td style="padding:24px 32px;background:#0f766e;color:#ffffff;">
                <div style="font-size:20px;font-weight:700;">Appointment request</div>
                <div style="font-size:12px;opacity:0.9;margin-top:4px;">New booking submitted</div>
              </td>
            </tr>
            <tr>
              <td style="padding:28px 32px;">
                <div style="font-size:16px;font-weight:600;margin-bottom:8px;">Patient details</div>
                <div style="font-size:14px;color:#334155;line-height:1.6;">
                  <strong>Name:</strong> {name}<br />
                  <strong>Email:</strong> {email}<br />
                  <strong>Phone:</strong> {phone_text}<br />
                  <strong>Preferred Date:</strong> {date_text}<br />
                  <strong>Preferred Time:</strong> {time_text}<br />
                  <strong>Preferred Location:</strong> {location_text}<br />
                </div>
                <div style="margin-top:16px;font-size:14px;font-weight:600;">Message</div>
                <div style="margin-top:6px;font-size:14px;color:#475569;white-space:pre-line;">{message_text}</div>
              </td>
            </tr>
            <tr>
              <td style="padding:18px 32px;background:#f8fafc;font-size:12px;color:#94a3b8;">
                Reply directly to the patient email to follow up.
              </td>
            </tr>
          </table>
        </td>
      </tr>
    </table>
  </body>
</html>
"""
    return subject, text_body, html_body
