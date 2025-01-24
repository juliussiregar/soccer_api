from typing import Optional
from app.core.database import get_session
from app.models.official import Official
from app.models.team import Team
from app.models.team_official import TeamOfficial
from app.utils.date import get_now


class TeamRepository:
    def create(self, payload: dict, user_id: int) -> Team:
        with get_session() as db:
            try:
                # Cari official berdasarkan user_id
                official = db.query(Official).filter(Official.user_id == user_id).first()
                if not official:
                    raise Exception(f"No official found for user_id {user_id}")
                
                # Cek apakah official sudah memiliki tim
                existing_team = db.query(Team).join(TeamOfficial).filter(TeamOfficial.official_id == official.id).first()
                if existing_team:
                    raise Exception("This official already has a team.")
                
                # Buat tim baru
                team = Team(**payload)
                db.add(team)
                db.commit()  # Commit untuk mendapatkan ID tim

                # Ambil kembali objek team dari sesi untuk memastikan tetap terikat dengan sesi
                team = db.query(Team).filter(Team.id == team.id).first()

                # Buat entri di tabel TeamOfficial menggunakan id dari tabel officials
                team_official = TeamOfficial(team_id=team.id, official_id=official.id)
                db.add(team_official)
                db.commit()  # Commit untuk menyimpan hubungan di team_officials

                # Ambil kembali objek team_official untuk memastikan tetap terikat dengan sesi
                team_official = db.query(TeamOfficial).filter(
                    TeamOfficial.team_id == team.id,
                    TeamOfficial.official_id == official.id
                ).first()

                return team
            except Exception as e:
                db.rollback()  # Rollback transaksi jika terjadi kesalahan
                raise Exception(f"Failed to create team: {str(e)}")

    def find_by_id(self, team_id: int) -> Optional[Team]:
        with get_session() as db:
            return db.query(Team).filter(Team.id == team_id).one_or_none()

    def find_by_official_id(self, official_id: int) -> Optional[Team]:
        with get_session() as db:
            return db.query(Team).join(TeamOfficial).filter(TeamOfficial.official_id == official_id).one_or_none()

    def update(self, team_id: int, payload: dict) -> Optional[Team]:
        with get_session() as db:
            team = db.query(Team).filter(Team.id == team_id).first()
            if not team:
                return None

            for key, value in payload.items():
                if value is not None:
                    setattr(team, key, value)

            team.updated_at = get_now()
            db.commit()
            db.refresh(team)  # Pastikan objek tetap terikat dengan sesi
            return team

    def assign_official(self, team_id: int, official_id: int) -> TeamOfficial:
        with get_session() as db:
            # Cek apakah hubungan sudah ada
            existing_assignment = db.query(TeamOfficial).filter(
                TeamOfficial.team_id == team_id,
                TeamOfficial.official_id == official_id
            ).first()

            if existing_assignment:
                raise Exception("This official is already assigned to the team.")

            # Buat hubungan baru
            team_official = TeamOfficial(team_id=team_id, official_id=official_id)
            db.add(team_official)
            db.commit()

            # Ambil kembali objek team_official untuk memastikan tetap terikat dengan sesi
            team_official = db.query(TeamOfficial).filter(
                TeamOfficial.team_id == team_id,
                TeamOfficial.official_id == official_id
            ).first()

            return team_official

    def unassign_official(self, team_id: int, official_id: int) -> bool:
        with get_session() as db:
            assignment = db.query(TeamOfficial).filter(
                TeamOfficial.team_id == team_id,
                TeamOfficial.official_id == official_id
            ).first()

            if not assignment:
                raise Exception("No such assignment exists.")

            db.delete(assignment)
            db.commit()
            return True
        
    def find_team_by_user_id(self, user_id: int) -> Optional[Team]:
        with get_session() as db:
            return (
                db.query(Team)
                .join(TeamOfficial)
                .join(Official)
                .filter(Official.user_id == user_id)
                .one_or_none()
            )
    def update_team_by_user_id(self, user_id: int, payload: dict) -> Optional[Team]:
        """
        Update tim berdasarkan user_id dari tabel Official.
        """
        with get_session() as db:
            try:
                # Cari official berdasarkan user_id
                official = db.query(Official).filter(Official.user_id == user_id).first()
                if not official:
                    raise Exception(f"No official found for user_id {user_id}")

                # Cari tim yang terkait dengan official tersebut
                team = db.query(Team).join(TeamOfficial).filter(TeamOfficial.official_id == official.id).first()
                if not team:
                    raise Exception("No team found for this official.")

                # Update tim dengan data yang diberikan
                for key, value in payload.items():
                    if value is not None:
                        setattr(team, key, value)

                team.updated_at = get_now()
                db.commit()
                db.refresh(team)  # Pastikan objek tetap terikat dengan sesi
                return team
            except Exception as e:
                db.rollback()
                raise Exception(f"Failed to update team: {str(e)}")

