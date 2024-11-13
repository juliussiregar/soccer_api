# repositories/position.py

from typing import List, Optional
import uuid
from sqlalchemy.orm import Query
from app.core.database import get_session
from app.models.position import Position
from app.schemas.position import CreateNewPosition, UpdatePosition, PositionFilter
from sqlalchemy.orm import joinedload


# Repository untuk manajemen CRUD Position
class PositionRepository:
    
    # Mengambil data Position berdasarkan ID perusahaan dan ID posisi
    def get_position_by_id(self, position_id: int, company_id: uuid.UUID) -> Optional[Position]:
        """
        Mengambil data Position berdasarkan ID posisi dan ID perusahaan.
        
        Args:
            position_id (int): ID posisi.
            company_id (uuid.UUID): ID perusahaan.

        Returns:x
            Optional[Position]: Objek Position atau None jika tidak ditemukan.
        """
        with get_session() as db:
            position = (
                db.query(Position)
                .filter(Position.id == position_id, Position.company_id == company_id)
                .first()
            )
        return position

    # Memfilter query Position berdasarkan PositionFilter
    def filtered(self, query: Query, filter: PositionFilter) -> Query:
        if filter.search:
            query = query.filter(Position.name.contains(filter.search))
        if filter.company_id:
            query = query.filter(Position.company_id == filter.company_id)
        return query

    # Mendapatkan semua Position dengan filter, paginasi
    def get_all_filtered(self, filter: PositionFilter) -> List[Position]:
        """
        Mengambil daftar Position berdasarkan filter, dengan paginasi.

        Args:
            filter (PositionFilter): Filter untuk pencarian posisi.

        Returns:
            List[Position]: Daftar posisi sesuai filter.
        """
        with get_session() as db:
            query = db.query(Position).options(joinedload(Position.company))  # Join ke Company
            query = self.filtered(query, filter).order_by(Position.created_at.desc())

            if filter.limit:
                query = query.limit(filter.limit)

            if filter.page and filter.limit:
                offset = (filter.page - 1) * filter.limit
                query = query.offset(offset)

            return query.all()

    # Menghitung jumlah Position berdasarkan filter yang diterapkan
    def count_by_filter(self, filter: PositionFilter) -> int:
        with get_session() as db:
            query = db.query(Position)
            query = self.filtered(query, filter)
            return query.count()

    # Menambahkan data Position baru ke database
    def insert(self, payload: CreateNewPosition) -> Position:
        """
        Menambahkan data Position baru.

        Args:
            payload (CreateNewPosition): Data untuk posisi baru.

        Returns:
            Position: Objek posisi yang baru dibuat.
        """
        position = Position()
        position.company_id = payload.company_id
        position.name = payload.name
        position.description = payload.description

        with get_session() as db:
            db.add(position)
            db.flush()
            db.commit()
            db.refresh(position)

        return position

    # Memperbarui data Position berdasarkan ID
    def update(self, position_id: int, payload: UpdatePosition) -> Optional[Position]:
        """
        Memperbarui data Position berdasarkan ID posisi.

        Args:
            position_id (int): ID posisi yang akan diperbarui.
            payload (UpdatePosition): Data baru untuk posisi.

        Returns:
            Optional[Position]: Objek Position setelah diperbarui atau None jika tidak ditemukan.
        """
        with get_session() as db:
            position = db.query(Position).filter(Position.id == position_id).first()

            if not position:
                return None

            if payload.name is not None:
                position.name = payload.name
            if payload.description is not None:
                position.description = payload.description

            position.updated_at = get_now()
            db.commit()
            db.refresh(position)

        return position

    # Menghapus data Position berdasarkan ID
    def delete_position_by_id(self, position_id: int) -> Optional[Position]:
        """
        Menghapus data Position berdasarkan ID posisi.

        Args:
            position_id (int): ID posisi yang akan dihapus.

        Returns:
            Optional[Position]: Objek Position yang dihapus atau None jika tidak ditemukan.
        """
        with get_session() as db:
            position = db.query(Position).filter(Position.id == position_id).first()
            if position:
                db.delete(position)
                db.commit()
            return position
