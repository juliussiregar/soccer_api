from typing import List
from passlib.context import CryptContext
from sqlalchemy.orm import Query, joinedload
from sqlalchemy import or_

from app.core.database import get_session
from app.models.user import User
from app.models.role import Role, user_role_association

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthRepository:
    def find_by_id(self, id: int) -> User | None:
        """Menemukan pengguna berdasarkan ID unik mereka.
        
        Args:
            id (int): ID dari pengguna yang dicari.
        
        Returns:
            User | None: Mengembalikan objek User jika ditemukan, sebaliknya None.
        """
        with get_session() as db:
            return (
                db.query(User)
                .filter(User.id == id, User.deleted_at.is_(None))
                .one_or_none()
            )

    def find_by_username_or_email(self, identifier: str) -> User | None:
        """Menemukan pengguna berdasarkan username atau email dan memuat data company serta roles.
        
        Args:
            identifier (str): Username atau email yang ingin dicari.
        
        Returns:
            User | None: Mengembalikan objek User jika ditemukan, sebaliknya None.
        
        Penjelasan:
            Menggunakan `or_` untuk memungkinkan pencarian baik berdasarkan `username`
            atau `email`. Memastikan pengguna belum dihapus dengan memeriksa `deleted_at`.
            Memuat data `company` dan `roles` secara bersamaan menggunakan `joinedload`.
        """
        with get_session() as db:
            return (
                db.query(User)
                .filter(
                    or_(User.username == identifier, User.email == identifier),
                    User.deleted_at.is_(None)
                )
                .options(joinedload(User.company), joinedload(User.roles))  # Memuat data `company` dan `roles` secara bersamaan
                .one_or_none()
            )

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Memverifikasi kata sandi yang diberikan dengan kata sandi yang di-hash.
        
        Args:
            plain_password (str): Kata sandi biasa yang akan diverifikasi.
            hashed_password (str): Kata sandi yang sudah di-hash di database.
        
        Returns:
            bool: Mengembalikan True jika kata sandi cocok, sebaliknya False.
        
        Penjelasan:
            Menggunakan `bcrypt_context.verify` untuk membandingkan kata sandi biasa
            yang diberikan dengan versi yang sudah di-hash di database.
        """
        return bcrypt_context.verify(plain_password, hashed_password)

    def find_by_id_with_roles(self, id: int) -> User | None:
        """Menemukan pengguna berdasarkan ID bersamaan dengan peran terkait.
        
        Args:
            id (int): ID dari pengguna yang dicari.
        
        Returns:
            User | None: Mengembalikan objek User beserta peran jika ditemukan, sebaliknya None.
        
        Penjelasan:
            Menggunakan `joinedload(User.roles)` untuk memuat data peran terkait secara bersamaan
            (eager loading) sehingga mengurangi query tambahan ke database.
        """
        with get_session() as db:
            return (
                db.query(User)
                .filter(User.id == id)
                .options(joinedload(User.roles))
                .one_or_none()
            )

    def has_role(self, id: int, role_name: str) -> bool:
        """Memeriksa apakah pengguna memiliki peran tertentu.
        
        Args:
            id (int): ID dari pengguna.
            role_name (str): Nama peran yang ingin diperiksa.
        
        Returns:
            bool: Mengembalikan True jika pengguna memiliki peran tersebut, sebaliknya False.
        
        Penjelasan:
            Menggunakan `find_by_id_with_roles` untuk mendapatkan pengguna beserta peran mereka.
            Mengembalikan True jika ada peran yang cocok dengan `role_name`, sebaliknya False.
        """
        user = self.find_by_id_with_roles(id)
        if user is None or not user.roles:
            return False
        return any(role.name == role_name for role in user.roles)

    def is_username_or_email_used(self, username: str, email: str, except_id: int = 0) -> bool:
        """Memeriksa apakah username atau email sudah digunakan, dengan pengecualian pada ID tertentu.
        
        Args:
            username (str): Username yang ingin diperiksa.
            email (str): Email yang ingin diperiksa.
            except_id (int, optional): ID pengguna yang akan dikecualikan dari pemeriksaan.
        
        Returns:
            bool: Mengembalikan True jika username atau email sudah digunakan, sebaliknya False.
        
        Penjelasan:
            Menghitung berapa kali `username` atau `email` yang diberikan ditemukan di database,
            tetapi mengecualikan pengguna dengan ID tertentu, untuk memungkinkan pembaruan data
            tanpa menyebabkan konflik data duplikat.
        """
        with get_session() as db:
            username_or_email_count = (
                db.query(User)
                .filter(
                    or_(User.username == username, User.email == email),
                    User.id != except_id
                )
                .count()
            )
        return username_or_email_count > 0
