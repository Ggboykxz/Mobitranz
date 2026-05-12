import structlog
from celery import Celery

from backend.config import settings

logger = structlog.get_logger()

celery_app = Celery(
    "mobitranz",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=[
        "backend.tasks.payment_tasks",
        "backend.tasks.notification_tasks",
        "backend.tasks.ministry_tasks",
    ],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Africa/Libreville",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,
    task_soft_time_limit=240,
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
)

logger.info("Celery app initialisée", broker=settings.redis_url)
