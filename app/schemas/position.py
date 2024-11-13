# schemas/position.py

from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# Filter untuk pencarian data Position dengan paginasi dan pencarian
class PositionFilter(BaseModel):
    limit: Optional[int] = None       # Batas jumlah hasil per halaman
    page: Optional[int] = None        # Nomor halaman
    search: Optional[str] = None      # Kata kunci untuk pencarian
    company_id: Optional[str] = None  # ID Perusahaan untuk filter HR

# Schema dasar untuk data Position
class CreateNewPosition(BaseModel):
    company_id: Optional[str] = None  # Membuat company_id opsional
    name: str                        # Nama Posisi
    description: Optional[str] = None # Deskripsi Posisi

# Schema untuk pembaruan data Position
class UpdatePosition(BaseModel):
    name: Optional[str] = None       # Nama Posisi (opsional untuk pembaruan)
    description: Optional[str] = None # Deskripsi Posisi (opsional untuk pembaruan)

# Schema lengkap untuk data Position yang diambil dari database
class PositionData(BaseModel):
    id: int                          # ID Posisi
    company_id: str                  # ID Perusahaan
    name: str                        # Nama Posisi
    description: Optional[str]       # Deskripsi Posisi
    created_at: datetime             # Tanggal pembuatan
    updated_at: Optional[datetime]   # Tanggal pembaruan terakhir

    class Config:
        from_attributes = True  # Konfigurasi untuk ORM mode agar dapat bekerja dengan SQLAlchemy
