"""SMTP email delivery.

Synchronous by design: this module is only ever called from inside a
Celery task (a separate worker process), so blocking I/O here doesn't
stall the FastAPI event loop. Never call this directly from an API
route — dispatch a Celery task instead (see app.workers.tasks).
"""

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


def send_email(*, to_email: str, subject: str, html_body: str, text_body: str) -> None:
    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = f"{settings.SMTP_FROM_NAME} <{settings.SMTP_FROM_EMAIL}>"
    message["To"] = to_email
    message.attach(MIMEText(text_body, "plain"))
    message.attach(MIMEText(html_body, "html"))

    try:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=10) as server:
            if settings.SMTP_USE_TLS:
                server.starttls()
            if settings.SMTP_USERNAME and settings.SMTP_PASSWORD:
                server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
            server.sendmail(settings.SMTP_FROM_EMAIL, [to_email], message.as_string())
        logger.info("email_sent", to=to_email, subject=subject)
    except Exception:
        logger.exception("email_send_failed", to=to_email, subject=subject)
        raise


def send_verification_email(*, to_email: str, full_name: str, token: str) -> None:
    verify_url = f"{settings.EMAIL_VERIFICATION_URL}?token={token}"
    send_email(
        to_email=to_email,
        subject="Verify your DevFlow AI account",
        text_body=(
            f"Hi {full_name},\n\n"
            f"Please verify your email address by visiting:\n{verify_url}\n\n"
            f"This link expires in 24 hours.\n\nDevFlow AI"
        ),
        html_body=f"""
        <div style="font-family: sans-serif; max-width: 480px; margin: 0 auto;">
            <h2>Welcome to DevFlow AI, {full_name}</h2>
            <p>Please verify your email address to activate your account.</p>
            <p><a href="{verify_url}" style="background:#4F46E5;color:#fff;padding:12px 24px;
               border-radius:6px;text-decoration:none;">Verify email</a></p>
            <p style="color:#666;font-size:13px;">This link expires in 24 hours.</p>
        </div>
        """,
    )


def send_password_reset_email(*, to_email: str, full_name: str, token: str) -> None:
    reset_url = f"{settings.PASSWORD_RESET_URL}?token={token}"
    send_email(
        to_email=to_email,
        subject="Reset your DevFlow AI password",
        text_body=(
            f"Hi {full_name},\n\n"
            f"We received a request to reset your password. Visit:\n{reset_url}\n\n"
            f"This link expires in 30 minutes. If you didn't request this, ignore this email.\n\n"
            f"DevFlow AI"
        ),
        html_body=f"""
        <div style="font-family: sans-serif; max-width: 480px; margin: 0 auto;">
            <h2>Reset your password</h2>
            <p>Hi {full_name}, we received a request to reset your password.</p>
            <p><a href="{reset_url}" style="background:#4F46E5;color:#fff;padding:12px 24px;
               border-radius:6px;text-decoration:none;">Reset password</a></p>
            <p style="color:#666;font-size:13px;">
               This link expires in 30 minutes. If you didn't request this, ignore this email.
            </p>
        </div>
        """,
    )
