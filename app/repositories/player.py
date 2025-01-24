from typing import Optional, List
from app.core.database import get_session
from app.models.guardian import Guardian
from app.models.guardian_player import GuardianPlayer
from app.models.player import Player
from app.models.team_player import TeamPlayer
from app.utils.date import get_now


class PlayerRepository:
    def create(self, payload: dict) -> Player:
        with get_session() as db:
            player = Player(**payload)
            db.add(player)
            db.commit()
            db.refresh(player)
            return player

    def find_by_id(self, player_id: int) -> Optional[Player]:
        with get_session() as db:
            return db.query(Player).filter(Player.id == player_id).one_or_none()

    def find_by_guardian_id(self, user_id: int) -> List[Player]:
        with get_session() as db:
            return db.query(Player).join(
                GuardianPlayer, GuardianPlayer.player_id == Player.id
            ).join(
                Guardian, Guardian.id == GuardianPlayer.guardian_id
            ).filter(
                Guardian.user_id == user_id  # Filter berdasarkan user_id dari tabel Guardian
            ).all()



    def list_all(self, limit: int, offset: int) -> List[Player]:
        with get_session() as db:
            return db.query(Player).offset(offset).limit(limit).all()

    def count_all(self) -> int:
        with get_session() as db:
            return db.query(Player).count()

    def update(self, player_id: int, payload: dict) -> Optional[Player]:
        with get_session() as db:
            player = db.query(Player).filter(Player.id == player_id).first()
            if not player:
                return None

            for key, value in payload.items():
                if value is not None:
                    setattr(player, key, value)

            player.updated_at = get_now()
            db.commit()
            db.refresh(player)
            return player

    def delete(self, player_id: int) -> bool:
        with get_session() as db:
            player = db.query(Player).filter(Player.id == player_id).first()
            if not player:
                return False

            db.delete(player)
            db.commit()
            return True

    def create_guardian_player(self, guardian_id: int, player_id: int) -> None:
        with get_session() as db:
            guardian_player = GuardianPlayer(guardian_id=guardian_id, player_id=player_id)
            db.add(guardian_player)
            db.commit()
            
    def find_by_team_id(self, team_id: int) -> List[Player]:
        with get_session() as db:
            return db.query(Player).join(
                TeamPlayer, TeamPlayer.player_id == Player.id
            ).filter(
                TeamPlayer.team_id == team_id
            ).all()
