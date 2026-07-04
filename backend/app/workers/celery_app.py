"""Celery application instance.

AI feature tasks (documentation generation, code review, bug detection,
sprint planning) run as background jobs so API requests return
immediately with a job reference instead of blocking on LLM latency.
"""

from celery import Celery

from app.core.config import settings

celery_app = Celery(
    "devflow_ai",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,
    task_soft_time_limit=270,
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=100,
    result_expires=86400,
)

# Task modules are registered here as they are implemented.
celery_app.autodiscover_tasks(["app.workers"], related_name="tasks")
