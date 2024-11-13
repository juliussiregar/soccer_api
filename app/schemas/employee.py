# schemas/employee.py

from pydantic import BaseModel
from typing import List, Optional
from datetime import date, datetime

# Filter untuk pencarian data Employee dengan paginasi dan pencarian
class EmployeeFilter(BaseModel):
    limit: Optional[int] = None  # Batas jumlah hasil per halaman
    page: Optional[int] = None   # Nomor halaman
    search: Optional[str] = None # Kata kunci untuk pencarian

# Schema dasar untuk data Employee
class CreateNewEmployee(BaseModel):
    user_name: Optional[str] = None   # Username dari Employee
    full_name: str                    # Nama lengkap Employee
    nik: str                          # Nomor Induk Karyawan
    email: str                        # Email Employee
    position: str                     # Jabatan Employee
    company_name: Optional[str] = None # Nama Perusahaan Employee

# Schema untuk mendapatkan data Employee berdasarkan username dan NIK
class GetEmployee(BaseModel):
    user_name: str  # Username dari Employee
    nik: str        # NIK dari Employee
