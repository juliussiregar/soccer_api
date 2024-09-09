from pydantic import BaseModel
from typing import Optional


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


class UserAddRole(BaseModel):
    role: str


class UserRemoveRole(BaseModel):
    role: str



class RekanRegister(BaseModel):
    full_name: str
    username: str
    email: Optional[str] = None
    role: Optional[str] = None


class RegisterUpdate(BaseModel):
    password: str

class PasswordUpdate(BaseModel):
    new_password: str
    confirm_password:str
