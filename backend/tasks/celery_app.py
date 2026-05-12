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
        "backend.tasks.backup_tasks",
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

celery_app.conf.beat_schedule = {
    "backup-database-daily": {
        "task": "backup_tasks.run_backup",
        "schedule": crontab(hour=2, minute=0),
        "options": {"queue": "backup"},
    },
    "generate-ministry-report-monthly": {
        "task": "ministry_tasks.generate_monthly_report",
        "schedule": crontab(day=1, hour=3, minute=0),
    },
}

from celery.schedules import crontab

logger.info("Celery app initialisee", broker=settings.redis_url)
