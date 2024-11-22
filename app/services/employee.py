# services/employee.py

from typing import List, Tuple
import uuid

from app.clients.face_api import FaceApiClient
from app.repositories.company import CompanyRepository
from app.repositories.employee import EmployeeRepository
from app.schemas.employee import EmployeeFilter, CreateNewEmployee, UpdateEmployee, EmployeeData
from app.schemas.faceapi_mgt import CreateEnrollFace, DeleteFace
from app.utils.exception import UnprocessableException, InternalErrorException
from app.utils.logger import logger


class EmployeeService:
    def __init__(self):
        self.company_repo = CompanyRepository()
        self.face_api_clients = FaceApiClient()
        self.employee_repo = EmployeeRepository()

    def create_employee(self, payload: CreateNewEmployee) -> EmployeeData:
        # Validasi: Cek apakah email sudah digunakan
        if self.employee_repo.is_email_used(payload.email):
            raise UnprocessableException(f"Email '{payload.email}' is already in use.")

        # Validasi: Cek apakah NIK sudah digunakan
        if self.employee_repo.is_nik_used(payload.nik):
            raise UnprocessableException(f"NIK '{payload.nik}' is already in use.")

        # Validasi: Pastikan company_id valid jika disediakan
        if payload.company_id and not self.company_repo.get_company_by_id(payload.company_id):
            raise UnprocessableException(f"Company ID '{payload.company_id}' does not exist.")

        # Validasi lainnya (misalnya position_id, format foto, dsb.)
        if not payload.photo:
            raise UnprocessableException("Photo is required to create a new employee.")

        try:
            # Simpan karyawan di database
            employee, face = self.employee_repo.insert(payload)

            # Panggil Face API untuk enroll wajah
            trx_id = uuid.uuid4()
            enroll = CreateEnrollFace(
                user_id=str(employee.nik),
                user_name=employee.user_name,
                facegallery_id=str(employee.company_id),
                image=payload.photo,
                trx_id=str(trx_id)
            )
            self.face_api_clients.insert_faces_visitor(enroll)

        except Exception as e:
            logger.error(f"Failed to create employee: {str(e)}")
            raise InternalErrorException("An error occurred while creating the employee.")

        # Kembalikan data karyawan
        employee_data = EmployeeData.from_orm(employee)
        employee_data.photo = face.photo if face else None
        return employee_data

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
        # Validasi: Pastikan karyawan ada
        employee = self.employee_repo.get_employee_by_id(employee_id)
        if not employee:
            raise UnprocessableException(f"Employee with ID '{employee_id}' not found.")

        # Cek apakah ada perubahan pada user_name atau nik
        if payload.user_name and payload.user_name != employee.user_name:
            # Validasi: Cek apakah user_name sudah digunakan oleh karyawan lain
            if self.employee_repo.is_user_name_used(payload.user_name, except_id=str(employee_id)):
                raise UnprocessableException(f"User name '{payload.user_name}' is already in use.")

        if payload.nik and payload.nik != employee.nik:
            # Validasi: Cek apakah NIK sudah digunakan oleh karyawan lain
            if self.employee_repo.is_nik_used(payload.nik, except_id=str(employee_id)):
                raise UnprocessableException(f"NIK '{payload.nik}' is already in use.")

        # Validasi: Cek apakah email sudah digunakan oleh karyawan lain jika ada perubahan
        if payload.email and payload.email != employee.email:
            if self.employee_repo.is_email_used(payload.email, except_id=str(employee_id)):
                raise UnprocessableException(f"Email '{payload.email}' is already in use.")

        try:
            # Cek apakah ada perubahan pada nik, atau photo yang mempengaruhi face
            should_reregister_face = False

            if payload.nik and payload.nik != employee.nik:
                should_reregister_face = True

            if payload.photo and payload.photo != (employee.face[0].photo if employee.face else None):
                should_reregister_face = True

            # Jika ada perubahan yang mempengaruhi face, maka hapus wajah dan daftarkan ulang
            if should_reregister_face:
                company = self.company_repo.get_company_by_employee_id(employee_id)
                if not company:
                    raise UnprocessableException("Associated company not found.")

                # Hapus data wajah lama
                trx_id_delete = uuid.uuid4()
                delete_face_employee = DeleteFace(
                    user_id=str(employee.nik),
                    facegallery_id=str(company.id),
                    trx_id=str(trx_id_delete),
                )
                self.face_api_clients.delete_face(delete_face_employee)

                # Update karyawan di database
                updated_employee = self.employee_repo.update(employee_id, payload)

                # Daftarkan ulang wajah setelah perubahan
                trx_id_create = uuid.uuid4()
                enroll = CreateEnrollFace(
                    user_id=str(updated_employee.nik),
                    user_name=updated_employee.user_name,
                    facegallery_id=str(updated_employee.company_id),
                    image=payload.photo,
                    trx_id=str(trx_id_create),
                )
                self.face_api_clients.insert_faces_visitor(enroll)

            else:
                # Jika tidak ada perubahan yang mempengaruhi face, cukup update karyawan
                updated_employee = self.employee_repo.update(employee_id, payload)

        except Exception as e:
            logger.error(f"Failed to update employee: {str(e)}")
            raise InternalErrorException("An error occurred while updating the employee.")

        # Ambil data photo setelah update
        # Pastikan mengambil foto dengan benar jika ada lebih dari satu entri wajah
        face = self.employee_repo.get_employee_by_id(employee_id).face
        employee_data = EmployeeData.from_orm(updated_employee)
        employee_data.photo = face[
            0].photo if face else None  # Mengambil foto dari elemen pertama jika face adalah list
        return employee_data

    def delete_employee(self, employee_id: uuid.UUID) -> EmployeeData:
        try:
            get_employee = self.employee_repo.get_employee_by_id(employee_id)
            if get_employee is None:
                raise UnprocessableException("Employee ID not found")

            company = self.company_repo.get_company_by_employee_id(employee_id)

            if company is None:
                raise UnprocessableException("Company not found")

            # Generate ID transaksi unik
            trx_id = uuid.uuid4()

            # Siapkan data untuk Face API
            delete_face_employee = DeleteFace(
                user_id=str(get_employee.nik),
                facegallery_id=str(company.id),
                trx_id=str(trx_id)
            )

            # Panggil Face API untuk menghapus data wajah
            face_api_response, _ = self.face_api_clients.delete_face(delete_face_employee)

            employee = self.employee_repo.delete_employee_by_id(employee_id)

            if employee is None:
                raise UnprocessableException("Employee not found")
        except Exception as e:
            raise InternalErrorException(str(e))

        # Kembalikan data karyawan
        return EmployeeData.from_orm(employee)

    def get_employees_by_company_id(self, company_id: uuid.UUID) -> List[EmployeeData]:
        employees = self.employee_repo.get_employees_by_company_id(company_id)
        if not employees:
            raise UnprocessableException("No employees found for this company")
        return [EmployeeData.from_orm(emp) for emp in employees]
