from celery import Celery

import celery_config
from config import celery_worker_settings


app = Celery(
    celery_worker_settings.worker_name,
    broker=celery_worker_settings.broker_uri,
    backend=celery_worker_settings.backend_uri,
    include=["tasks"],
)
app.config_from_object(celery_config)
