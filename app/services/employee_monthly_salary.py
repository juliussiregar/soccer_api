# services/employee_monthly_salary.py
from decimal import Decimal
from typing import List, Tuple
import uuid
from app.repositories.employee_monthly_salary import EmployeeMonthlySalaryRepository
from app.schemas.employee_monthly_salary import CreateNewEmployeeMonthlySalary, UpdateEmployeeMonthlySalary, \
    EmployeeMonthlySalaryData, EmployeeMonthlySalaryFilter
from app.utils.exception import UnprocessableException, InternalErrorException
from app.repositories.employee_daily_salary import EmployeeDailySalaryRepository
from datetime import datetime

from app.utils.logger import logger


class EmployeeMonthlySalaryService:
    def __init__(
        self,
        employee_daily_salary_repo: EmployeeDailySalaryRepository,
        employee_monthly_salary_repo: EmployeeMonthlySalaryRepository,
    ):
        self.employee_daily_salary_repo = employee_daily_salary_repo
        self.employee_monthly_salary_repo = employee_monthly_salary_repo

    def create_or_update_monthly_salary(self, month: int, year: int):
        """Membuat atau memperbarui gaji bulanan berdasarkan query SQL"""
        try:
            # Ambil data total gaji bulanan langsung dari query SQL
            monthly_salaries = self.employee_monthly_salary_repo.get_total_monthly_salary_by_employee(month, year)

            for salary_data in monthly_salaries:
                employee_id = salary_data.employee_id
                normal_salary = salary_data.normal_salary
                total_salary = salary_data.total_monthly_salary

                # Cek apakah gaji bulanan sudah ada
                existing_monthly_salary = self.employee_monthly_salary_repo.get_by_employee_id_and_month_year(
                    employee_id, month, year
                )

                if existing_monthly_salary:
                    # Update data gaji bulanan
                    updated_salary = UpdateEmployeeMonthlySalary(
                        normal_salary=normal_salary,
                        total_salary=total_salary,
                    )
                    self.employee_monthly_salary_repo.update(existing_monthly_salary.id, updated_salary)
                    logger.info(f"Updated monthly salary for employee {employee_id}")
                else:
                    # Insert data gaji bulanan baru
                    new_salary_payload = CreateNewEmployeeMonthlySalary(
                        employee_id=employee_id,
                        month=month,
                        year=year,
                        normal_salary=normal_salary,
                        total_salary=total_salary,
                    )
                    self.employee_monthly_salary_repo.insert(new_salary_payload)
                    logger.info(f"Inserted monthly salary for employee {employee_id}")

        except Exception as e:
            logger.error(f"Error creating or updating monthly salary: {str(e)}")
            raise InternalErrorException("Failed to create or update monthly salary.")

    # def create_or_update_monthly_salary(self, employee_id: uuid.UUID, month: int, year: int):
    #     """
    #     Membuat atau memperbarui gaji bulanan berdasarkan data gaji harian.
    #     """
    #     # Ambil semua gaji harian untuk karyawan tertentu pada bulan dan tahun
    #     daily_salaries = self.employee_daily_salary_repo.get_all_by_month_year(employee_id, month, year)
    #
    #     if not daily_salaries:
    #         raise UnprocessableException(f"No daily salary data found for employee {employee_id} in {month}/{year}")
    #
    #     # Hitung total gaji bulanan
    #     total_salary = sum(daily.total_salary for daily in daily_salaries)
    #
    #     # Ambil data gaji bulanan yang sudah ada (jika ada)
    #     existing_monthly_salary = self.employee_monthly_salary_repo.get_by_employee_id_and_month_year(employee_id,
    #                                                                                                   month, year)
    #
    #     if existing_monthly_salary:
    #         # Perbarui data gaji bulanan
    #         existing_monthly_salary.total_salary = total_salary
    #         existing_monthly_salary.updated_at = datetime.now()
    #
    #         try:
    #             updated_salary = self.employee_monthly_salary_repo.update(existing_monthly_salary.id,
    #                                                                       existing_monthly_salary)
    #             return updated_salary
    #         except Exception as e:
    #             raise InternalErrorException(f"Error updating monthly salary: {str(e)}")
    #     else:
    #         # Buat data baru jika belum ada
    #         payload = CreateNewEmployeeMonthlySalary(
    #             employee_id=employee_id,
    #             month=month,
    #             year=year,
    #             normal_salary=daily_salaries[0].normal_salary,  # Asumsi sama untuk semua hari
    #             total_salary=Decimal(total_salary),
    #         )
    #         return self.employee_monthly_salary_repo.insert(payload)

    def get_employee_monthly_salary(self, employee_monthly_salary_id: int) -> EmployeeMonthlySalaryData:
        """Mendapatkan data gaji bulanan berdasarkan ID"""
        employee_monthly_salary = self.employee_monthly_salary_repo.get_employee_monthly_salary_by_id(employee_monthly_salary_id)
        if employee_monthly_salary is None:
            raise UnprocessableException("EmployeeMonthlySalary not found")
        return employee_monthly_salary

    def list_employee_monthly_salaries(self, filter: EmployeeMonthlySalaryFilter) -> Tuple[List[EmployeeMonthlySalaryData], int, int]:
        """Mendapatkan daftar gaji bulanan dengan filter"""
        monthly_salaries = self.employee_monthly_salary_repo.get_all_filtered(filter)
        total_rows = self.employee_monthly_salary_repo.count_by_filter(filter)
        total_pages = (total_rows + filter.limit - 1) // filter.limit if filter.limit else 1
        return monthly_salaries, total_rows, total_pages

    def update_employee_monthly_salary(self, employee_monthly_salary_id: int, payload: UpdateEmployeeMonthlySalary) -> EmployeeMonthlySalaryData:
        """Memperbarui data gaji bulanan"""
        employee_monthly_salary = self.employee_monthly_salary_repo.update(employee_monthly_salary_id, payload)
        if employee_monthly_salary is None:
            raise UnprocessableException("EmployeeMonthlySalary not found or could not be updated")
        return employee_monthly_salary

    def delete_employee_monthly_salary(self, employee_monthly_salary_id: int) -> EmployeeMonthlySalaryData:
        """Menghapus data gaji bulanan berdasarkan ID"""
        employee_monthly_salary = self.employee_monthly_salary_repo.delete_employee_monthly_salary_by_id(employee_monthly_salary_id)
        if employee_monthly_salary is None:
            raise UnprocessableException("EmployeeMonthlySalary not found")
        return employee_monthly_salary
