# services/employee_daily_salary.py

from typing import List, Tuple
import uuid
from app.repositories.employee_daily_salary import EmployeeDailySalaryRepository
from app.schemas.employee_daily_salary import EmployeeDailySalaryFilter, CreateNewEmployeeDailySalary, UpdateEmployeeDailySalary, EmployeeDailySalaryData
from app.utils.exception import UnprocessableException, InternalErrorException

class EmployeeDailySalaryService:
    def __init__(self):
        self.employee_daily_salary_repo = EmployeeDailySalaryRepository()

    def create_employee_daily_salary(self, payload: CreateNewEmployeeDailySalary) -> EmployeeDailySalaryData:
        # Validasi jika employee_id sudah ada
        if payload.employee_id and payload.work_date:
            existing_salary = self.employee_daily_salary_repo.get_by_employee_id_and_date(
                uuid.UUID(payload.employee_id),
                payload.work_date
            )
            if existing_salary:
                raise UnprocessableException(
                    "Employee Daily Salary for this employee already exists on the specified date.")

        # Insert jika validasi berhasil
        try:
            employee_daily_salary = self.employee_daily_salary_repo.insert(payload)
        except Exception as e:
            raise InternalErrorException(str(e))
        return employee_daily_salary

    def get_employee_daily_salary(self, employee_daily_salary_id: int) -> EmployeeDailySalaryData:
        employee_daily_salary = self.employee_daily_salary_repo.get_employee_daily_salary_by_id(employee_daily_salary_id)
        if employee_daily_salary is None:
            raise UnprocessableException("EmployeeDailySalary not found")
        return employee_daily_salary

    def list_employee_daily_salaries(self, filter: EmployeeDailySalaryFilter) -> Tuple[List[EmployeeDailySalaryData], int, int]:
        daily_salaries = self.employee_daily_salary_repo.get_all_filtered(filter)
        total_rows = self.employee_daily_salary_repo.count_by_filter(filter)
        total_pages = (total_rows + filter.limit - 1) // filter.limit if filter.limit else 1
        return daily_salaries, total_rows, total_pages

    def update_employee_daily_salary(self, employee_daily_salary_id: int, payload: UpdateEmployeeDailySalary) -> EmployeeDailySalaryData:
        employee_daily_salary = self.employee_daily_salary_repo.update(employee_daily_salary_id, payload)
        if employee_daily_salary is None:
            raise UnprocessableException("EmployeeDailySalary not found or could not be updated")
        return employee_daily_salary

    def delete_employee_daily_salary(self, employee_daily_salary_id: int) -> EmployeeDailySalaryData:
        employee_daily_salary = self.employee_daily_salary_repo.delete_employee_daily_salary_by_id(employee_daily_salary_id)
        if employee_daily_salary is None:
            raise UnprocessableException("EmployeeDailySalary not found")
        return employee_daily_salary

    def calculate_daily_salary(
            self, hours_worked: int, hourly_rate: int, late_deduction: int, overtime_hours: int, overtime_rate: int
    ) -> int:
        """
        Calculate daily salary.

        Formula:
        - Normal Salary = hours_worked * hourly_rate
        - Total Salary = Normal Salary - late_deduction + (overtime_hours * overtime_rate)
        """
        normal_salary = hours_worked * hourly_rate
        overtime_pay = overtime_hours * overtime_rate
        total_salary = normal_salary - late_deduction + overtime_pay
        return total_salary

    def create_employee_daily_salary_with_calculation(self,
                                                      payload: CreateNewEmployeeDailySalary) -> EmployeeDailySalaryData:
        # Example hourly rate and overtime rate (you can customize based on your use case)
        HOURLY_RATE = 50000  # Example hourly rate (IDR)
        OVERTIME_RATE = 75000  # Example overtime rate (IDR)

        # Validate the payload
        if not payload.hours_worked:
            raise UnprocessableException("Hours worked must be provided.")

        # Calculate salary components
        normal_salary = payload.hours_worked * HOURLY_RATE
        total_salary = self.calculate_daily_salary(
            hours_worked=payload.hours_worked,
            hourly_rate=HOURLY_RATE,
            late_deduction=payload.late_deduction or 0,
            overtime_hours=payload.overtime_pay // OVERTIME_RATE if payload.overtime_pay else 0,
            overtime_rate=OVERTIME_RATE,
        )

        # Prepare payload with calculated salary
        payload.normal_salary = normal_salary
        payload.total_salary = total_salary

        # Insert into the database
        return self.create_employee_daily_salary(payload)
