import os

from celery import Celery
from celery.schedules import crontab

from app.core.config import settings

# Inisialisasi Celery untuk API
celery_app = Celery(
    "periodic_tasks",
    broker=settings.celery_broker_url
)

# Konfigurasi Celery
celery_app.conf.update(
    result_backend=settings.celery_result_backend,
    result_expires=3600,  # Mengatur waktu expired hasil task
    timezone='Asia/Jakarta',  # Zona waktu
    beat_schedule={
        'calculate_monthly_salary_every_month': {
            'task': 'app.services.employee_monthly_salary_periodic.calculate_monthly_salary_periodic',  # Nama task yang akan dijalankan
            'schedule': crontab(minute="0", hour="0"),  # Menjalankan task setiap hari pada jam 00:00
            # 'schedule': crontab(minute="*"),  # Menjalankan task setiap menit
        },
    },
    imports=['app.services.employee_monthly_salary_periodic'],
)

celery_app.conf.broker_connection_retry_on_startup = True