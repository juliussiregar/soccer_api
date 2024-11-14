# services/daily_salary.py

from typing import List, Tuple
import uuid
from app.repositories.daily_salary import DailySalaryRepository
from app.schemas.daily_salary import DailySalaryFilter, CreateNewDailySalary, UpdateDailySalary, DailySalaryData
from app.utils.exception import UnprocessableException, InternalErrorException

class DailySalaryService:
    def __init__(self):
        self.daily_salary_repo = DailySalaryRepository()

    def create_daily_salary(self, payload: CreateNewDailySalary) -> DailySalaryData:
        # Validasi jika employee_id sudah ada
        if payload.employee_id:
            existing_salary = self.daily_salary_repo.get_by_employee_id(uuid.UUID(payload.employee_id))
            if existing_salary:
                raise UnprocessableException("Daily Salary for this employee already exists.")
        
        # Validasi jika position_id sudah ada
        if payload.position_id:
            existing_salary = self.daily_salary_repo.get_by_position_id(payload.position_id)
            if existing_salary:
                raise UnprocessableException("Daily Salary for this position already exists.")

        # Insert jika validasi berhasil
        try:
            daily_salary = self.daily_salary_repo.insert(payload)
        except Exception as e:
            raise InternalErrorException(str(e))
        return daily_salary

    def get_daily_salary(self, daily_salary_id: int) -> DailySalaryData:
        daily_salary = self.daily_salary_repo.get_daily_salary_by_id(daily_salary_id)
        if daily_salary is None:
            raise UnprocessableException("DailySalary not found")
        return daily_salary

    def list_daily_salaries(self, filter: DailySalaryFilter) -> Tuple[List[DailySalaryData], int, int]:
        daily_salaries = self.daily_salary_repo.get_all_filtered(filter)
        total_rows = self.daily_salary_repo.count_by_filter(filter)
        total_pages = (total_rows + filter.limit - 1) // filter.limit if filter.limit else 1
        return daily_salaries, total_rows, total_pages

    def update_daily_salary(self, daily_salary_id: int, payload: UpdateDailySalary) -> DailySalaryData:
        daily_salary = self.daily_salary_repo.update(daily_salary_id, payload)
        if daily_salary is None:
            raise UnprocessableException("DailySalary not found or could not be updated")
        return daily_salary

    def delete_daily_salary(self, daily_salary_id: int) -> DailySalaryData:
        daily_salary = self.daily_salary_repo.delete_daily_salary_by_id(daily_salary_id)
        if daily_salary is None:
            raise UnprocessableException("DailySalary not found")
        return daily_salary
