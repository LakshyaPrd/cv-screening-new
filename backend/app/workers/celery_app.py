"""
Celery application for async task processing.
For production use - currently using FastAPI BackgroundTasks for simplicity.
"""
from celery import Celery
from app.config import settings

# Create Celery app
celery_app = Celery(
    "cv_screening",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

# Configure Celery
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    result_expires=3600,  # 1 hour
)

# Auto-discover tasks
celery_app.autodiscover_tasks(['app.workers'])
