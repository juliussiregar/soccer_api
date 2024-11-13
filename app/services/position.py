# services/position.py

from typing import List, Tuple
import uuid
from app.repositories.position import PositionRepository
from app.schemas.position import PositionFilter, CreateNewPosition, UpdatePosition, PositionData
from app.utils.exception import UnprocessableException, InternalErrorException
from app.utils.logger import logger

# Service untuk manajemen data Position
class PositionService:
    def __init__(self) -> None:
        # Inisialisasi repository Position
        self.position_repo = PositionRepository()

    # Menambahkan posisi baru
    def create_position(self, payload: CreateNewPosition) -> PositionData:
        """
        Menambahkan data Position baru.

        Args:
            payload (CreateNewPosition): Data untuk posisi baru.

        Returns:
            PositionData: Objek Position yang baru dibuat.
        """
        try:
            position = self.position_repo.insert(payload)
        except Exception as err:
            err_msg = str(err)
            logger.error(err_msg)
            raise InternalErrorException(err_msg)

        return position

    # Mendapatkan posisi berdasarkan ID dan ID perusahaan
    def get_position(self, position_id: int, company_id: uuid.UUID) -> PositionData:
        """
        Mengambil data Position berdasarkan ID dan ID perusahaan.

        Args:
            position_id (int): ID posisi.
            company_id (uuid.UUID): ID perusahaan.

        Returns:
            PositionData: Data posisi yang diambil.
        """
        position = self.position_repo.get_position_by_id(position_id, company_id)
        if position is None:
            raise UnprocessableException("Position not found")
        return position

    # Mendapatkan daftar posisi dengan filter dan paginasi
    def list_positions(self, filter: PositionFilter) -> Tuple[List[PositionData], int, int]:
        """
        Mendapatkan daftar posisi berdasarkan filter dan paginasi.

        Args:
            filter (PositionFilter): Filter untuk pencarian posisi.

        Returns:
            Tuple[List[PositionData], int, int]: Daftar posisi, total rows, dan total pages.
        """
        positions = self.position_repo.get_all_filtered(filter)
        total_rows = self.position_repo.count_by_filter(filter)
        total_pages = (total_rows + filter.limit - 1) // filter.limit if filter.limit else 1
        return positions, total_rows, total_pages


    # Memperbarui posisi berdasarkan ID
    def update_position(self, position_id: int, payload: UpdatePosition) -> PositionData:
        """
        Memperbarui data Position berdasarkan ID posisi.

        Args:
            position_id (int): ID posisi yang akan diperbarui.
            payload (UpdatePosition): Data baru untuk posisi.

        Returns:
            PositionData: Data posisi setelah diperbarui.
        """
        position = self.position_repo.update(position_id, payload)
        if position is None:
            raise UnprocessableException("Position not found or could not be updated")
        return position

    # Menghapus posisi berdasarkan ID
    def delete_position(self, position_id: int) -> PositionData:
        """
        Menghapus data Position berdasarkan ID posisi.

        Args:
            position_id (int): ID posisi yang akan dihapus.

        Returns:
            PositionData: Data posisi yang dihapus.
        """
        position = self.position_repo.delete_position_by_id(position_id)
        if position is None:
            raise UnprocessableException("Position not found")
        return position
