from uuid import UUID
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from typing import List, Optional  # Pastikan List diimpor dari typing

class UserFilter(BaseModel):
    limit: Optional[int] = None
    page: Optional[int] = None
    search: Optional[str] = None


class UserCreate(BaseModel):
    full_name: str
    username: str
    password: str
    email: Optional[str] = None
    role: Optional[str] = None


class UserUpdate(BaseModel):
    full_name: str
    username: str
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
    username: str
    email: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None
    roles: Optional[List[str]] = []  # Menambahkan atribut roles yang berisi list role

