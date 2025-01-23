from sqlalchemy.orm import Session
from app.models.revoked_token import RevokedToken
from app.core.database import get_session


class TokenRepository:
    def add_revoked_token(self, token: str):
        """
        Menambahkan token ke daftar revoked.
        """
        revoked_token = RevokedToken(token=token)
        with get_session() as db:
            db.add(revoked_token)
            db.commit()

    def is_token_revoked(self, token: str) -> bool:
        """
        Memeriksa apakah token telah di-revoke.
        """
        with get_session() as db:
            return db.query(RevokedToken).filter(RevokedToken.token == token).first() is not None
