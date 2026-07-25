from celery import Celery
from celery.schedules import crontab
from app.config import get_settings

settings = get_settings()

celery_app = Celery(
    "marketing_worker",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,
)

celery_app.conf.beat_schedule = {
    "publish-scheduled-posts": {
        "task": "app.tasks.publish.publish_scheduled",
        "schedule": 60.0,  # Every minute
    },
    "sync-social-metrics": {
        "task": "app.tasks.monitor.sync_metrics",
        "schedule": crontab(minute="*/30"),  # Every 30 minutes
    },
    "generate-daily-report": {
        "task": "app.tasks.report.generate_daily",
        "schedule": crontab(hour=23, minute=0),  # Daily at 11 PM
    },
    "detect-anomalies": {
        "task": "app.tasks.monitor.detect_anomalies",
        "schedule": crontab(minute="*/15"),  # Every 15 minutes
    },
    "suggest-weekly-content": {
        "task": "app.tasks.optimize.suggest_content",
        "schedule": crontab(hour=9, minute=0, day_of_week=1),  # Monday at 9 AM
    },
}
