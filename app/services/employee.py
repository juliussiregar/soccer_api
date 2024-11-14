# services/employee.py

from typing import List, Tuple
import uuid
from app.repositories.employee import EmployeeRepository
from app.schemas.employee import EmployeeFilter, CreateNewEmployee, UpdateEmployee, EmployeeData
from app.utils.exception import UnprocessableException, InternalErrorException

class EmployeeService:
    def __init__(self):
        self.employee_repo = EmployeeRepository()

    def create_employee(self, payload: CreateNewEmployee) -> EmployeeData:
        try:
            employee = self.employee_repo.insert(payload)
        except Exception as e:
            raise InternalErrorException(str(e))
        return employee

    def get_employee(self, employee_id: uuid.UUID) -> EmployeeData:
        employee = self.employee_repo.get_employee_by_id(employee_id)
        if employee is None:
            raise UnprocessableException("Employee not found")
        return employee

    def list_employees(self, filter: EmployeeFilter) -> Tuple[List[EmployeeData], int, int]:
        employees = self.employee_repo.get_all_filtered(filter)
        total_rows = self.employee_repo.count_by_filter(filter)
        total_pages = (total_rows + filter.limit - 1) // filter.limit if filter.limit else 1
        return employees, total_rows, total_pages

    def update_employee(self, employee_id: uuid.UUID, payload: UpdateEmployee) -> EmployeeData:
        employee = self.employee_repo.update(employee_id, payload)
        if employee is None:
            raise UnprocessableException("Employee not found or could not be updated")
        return employee

    def delete_employee(self, employee_id: uuid.UUID) -> EmployeeData:
        employee = self.employee_repo.delete_employee_by_id(employee_id)
        if employee is None:
            raise UnprocessableException("Employee not found")
        return employee
    
    def get_employees_by_company_id(self, company_id: uuid.UUID) -> List[EmployeeData]:
        employees = self.employee_repo.get_employees_by_company_id(company_id)
        if not employees:
            raise UnprocessableException("No employees found for this company")
        return [EmployeeData.from_orm(emp) for emp in employees]
