from datetime import datetime

from app.core.config import settings
from app.services.employee_monthly_salary import EmployeeMonthlySalaryService
from app.repositories.employee_daily_salary import EmployeeDailySalaryRepository
from app.repositories.employee_monthly_salary import EmployeeMonthlySalaryRepository

from celery import Celery
import os

celery_app = Celery(
    "periodic_tasks",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)

@celery_app.task
def calculate_monthly_salary_periodic():
    """Task Periodik untuk menghitung ulang gaji bulanan berdasarkan data harian"""
    current_month = datetime.now().month
    current_year = datetime.now().year

    employee_daily_salary_repo = EmployeeDailySalaryRepository()
    employee_monthly_salary_repo = EmployeeMonthlySalaryRepository()
    employee_monthly_salary_service = EmployeeMonthlySalaryService(
        employee_daily_salary_repo, employee_monthly_salary_repo
    )

    # Jalankan perhitungan gaji bulanan
    employee_monthly_salary_service.create_or_update_monthly_salary(current_month, current_year)
