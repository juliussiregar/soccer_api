from typing import Optional, List
from app.core.database import get_session
from app.models.player import Player
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

    def find_by_guardian_id(self, guardian_id: int) -> List[Player]:
        with get_session() as db:
            return db.query(Player).join(
                Player.guardian_player
            ).filter(
                Player.guardian_player.guardian_id == guardian_id
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
