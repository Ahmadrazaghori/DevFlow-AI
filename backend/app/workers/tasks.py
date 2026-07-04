"""Celery tasks.

Auth-related tasks live here for now. AI feature tasks (documentation
generation, code review, bug detection, sprint planning) are added in
the AI Engine phase.
"""

from app.infrastructure.email.email_service import send_password_reset_email, send_verification_email
from app.workers.celery_app import celery_app


@celery_app.task(name="send_verification_email_task", bind=True, max_retries=3)
def send_verification_email_task(self, *, to_email: str, full_name: str, token: str) -> None:
    try:
        send_verification_email(to_email=to_email, full_name=full_name, token=token)
    except Exception as exc:
        raise self.retry(exc=exc, countdown=30) from exc


@celery_app.task(name="send_password_reset_email_task", bind=True, max_retries=3)
def send_password_reset_email_task(self, *, to_email: str, full_name: str, token: str) -> None:
    try:
        send_password_reset_email(to_email=to_email, full_name=full_name, token=token)
    except Exception as exc:
        raise self.retry(exc=exc, countdown=30) from exc
