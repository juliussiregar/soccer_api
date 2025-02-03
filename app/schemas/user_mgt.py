from uuid import UUID
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from typing import List, Optional

from app.models.team_official import PositionEnum
class UserFilter(BaseModel):
    limit: Optional[int] = 20  # Default limit
    page: Optional[int] = 1  # Default page
    search: Optional[str] = None  # Query pencarian full_name

class UserCreate(BaseModel):
    email: str 
    password: str
    full_name: str
    role: str
    
    
class RegisterGuardian(BaseModel):
    full_name: str
    password: str
    email: str

    birth_date: datetime
    kartu_keluarga: str
    ktp: str
    phone_number: str
    address: str

    class Config:
        orm_mode = True
class RegisterOfficial(BaseModel):
    email: str
    password: str
    full_name: str
    position: str  
    profile_picture: Optional[str] = None

    class Config:
        orm_mode = True

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    password: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] = None

class UserAddRole(BaseModel):
    role: str


class UserRemoveRole(BaseModel):
    role: str


class RegisterUpdate(BaseModel):
    password: str

class PasswordUpdate(BaseModel):
    new_password: str
    confirm_password: str


class AuthUser(BaseModel):
    id: int
    full_name: str
    email: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None
    roles: Optional[List[str]] = []  # Menambahkan atribut roles yang berisi list role

