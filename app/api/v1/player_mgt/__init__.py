from fastapi import APIRouter

from app.api.v1.player_mgt import manage_player

router = APIRouter(tags=["Player Management"])

router.include_router(manage_player.router)
