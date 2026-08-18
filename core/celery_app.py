import os 

from celery import Celery
from celery.signals import setup_logging
from dotenv import load_dotenv

from core.config import get_settings
from core.logger import setup_applevel_logger


load_dotenv()
settings = get_settings()

celery_app = Celery(
    "sql-agent",
    broker=settings.broker_uri,
    backend=settings.backend_uri
)

app = celery_app

celery_app.conf.update(
    include=["core.tasks"],
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    worker_prefetch_multiplier=1,
    worker_hijack_root_logger=False,
    result_expires=settings.job_ttl_seconds,
    broker_connection_retry_on_startup=True,
    broker_pool_limit=20,
    broker_transport_options={"visibility_timeout": 7200},
    task_time_limit=1800,
    task_soft_time_limit=1500,
    worker_concurrency=settings.celery_concurrency,
)


@setup_logging.connect
def _configure_celery_logging(**kwargs):
    setup_applevel_logger(file_name=os.getenv("LOG_FILE", "sql-processing.log"))

celery_app.autodiscover_tasks(["core"])
