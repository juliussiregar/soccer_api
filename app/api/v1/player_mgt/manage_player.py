from fastapi import APIRouter, Depends, HTTPException
from typing import Annotated, Optional
from app.schemas.player import PlayerCreate, PlayerUpdate
from app.middleware.jwt import jwt_middleware, AuthUser
from app.schemas.user_mgt import UserRegister
from app.services.official import OfficialService
from app.services.player import PlayerService
from app.core.constants.auth import ROLE_ADMIN, ROLE_GUARDIAN, ROLE_OFFICIAL, ROLE_PLAYER
from app.services.user import UserService

router = APIRouter()
player_service = PlayerService()
official_service = OfficialService()
user_service = UserService()

@router.post("/player", description="Create a player profile (GUARDIAN only)")
def create_user_and_player(
    auth_user: Annotated[AuthUser, Depends(jwt_middleware)],
    user_body: UserRegister,
    player_body: PlayerCreate,
):
    # Hanya GUARDIAN yang dapat membuat user dan player profile
    if not auth_user.roles or ROLE_GUARDIAN not in auth_user.roles:
        raise HTTPException(
            status_code=403,
            detail="Access denied: Only GUARDIAN role can create a user and player profile."
        )

    try:
        # Step 1: Create a new user
        user = user_service.create(user_body)

        # Step 2: Create a new player associated with the user
        player_payload = player_body.dict()
        player_payload["user_id"] = user.id  # Associate player with the created user's ID
        player = player_service.create(player_payload, user_id=auth_user.id)

        return {
            "data": {
                "user": {
                    "id": user.id,
                    "full_name": user.full_name,
                    "username": user.username,
                    "roles": [user_body.role],
                    "created_at": user.created_at,
                    "updated_at": user.updated_at,
                },
                "player": {
                    "id": player.id,
                    "name": player.name,
                    "position": player.position,
                    "profile_picture": player.profile_picture,
                    "age": player.age,
                    "jersey_number": player.jersey_number,
                    "height": player.height,
                    "weight": player.weight,
                    "bio": player.bio,
                    "created_at": player.created_at,
                    "updated_at": player.updated_at,
                },
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/player/guardian", description="Get players by guardian ID (GUARDIAN only)")
def get_players_by_guardian(
    auth_user: Annotated[AuthUser, Depends(jwt_middleware)],
):
    # Only GUARDIAN can get players by guardian ID
    if not auth_user.roles or ROLE_GUARDIAN not in auth_user.roles:
        raise HTTPException(
            status_code=403,
            detail="Access denied: Only GUARDIAN role can view players they created."
        )

    try:
        players = player_service.find_by_guardian_id(auth_user.id)
        return {
            "data": [
                {
                    "id": player.id,
                    "name": player.name,
                    "position": player.position,
                    "profile_picture": player.profile_picture,
                    "age": player.age,
                    "jersey_number": player.jersey_number,
                    "height": player.height,
                    "weight": player.weight,
                    "bio": player.bio,
                    "created_at": player.created_at,
                    "updated_at": player.updated_at,
                }
                for player in players
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/players", description="Get all players (ADMIN only)")
def list_all_players(
    auth_user: Annotated[AuthUser, Depends(jwt_middleware)],
    limit: int = 20,
    page: int = 1,
):
    # Only ADMIN can view all players
    if not auth_user.roles or ROLE_ADMIN not in auth_user.roles:
        raise HTTPException(
            status_code=403,
            detail="Access denied: Only ADMIN role can view all players."
        )

    try:
        players, total = player_service.list_all(limit, page)
        total_pages = (total + limit - 1) // limit
        return {
            "data": [
                {
                    "id": player.id,
                    "name": player.name,
                    "position": player.position,
                    "profile_picture": player.profile_picture,
                    "age": player.age,
                    "jersey_number": player.jersey_number,
                    "height": player.height,
                    "weight": player.weight,
                    "bio": player.bio,
                    "created_at": player.created_at,
                    "updated_at": player.updated_at,
                }
                for player in players
            ],
            "meta": {
                "limit": limit,
                "page": page,
                "total_rows": total,
                "total_pages": total_pages,
            },
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/player", description="Update a player profile")
def update_player(
    auth_user: Annotated[AuthUser, Depends(jwt_middleware)],
    body: PlayerUpdate,
    player_id: Optional[int] = None,
):
    # GUARDIAN updates with player_id, PLAYER updates their own profile
    if not auth_user.roles or (ROLE_GUARDIAN not in auth_user.roles and ROLE_PLAYER not in auth_user.roles):
        raise HTTPException(
            status_code=403,
            detail="Access denied: Only GUARDIAN or PLAYER roles can update a player profile."
        )

    if ROLE_PLAYER in auth_user.roles:
        player_id = auth_user.id  # PLAYER updates their own profile
    elif ROLE_GUARDIAN in auth_user.roles and not player_id:
        raise HTTPException(
            status_code=400,
            detail="Player ID is required for GUARDIAN role."
        )

    try:
        payload = body.dict(exclude_unset=True)
        player = player_service.update(player_id, payload)
        return {
            "data": {
                "id": player.id,
                "name": player.name,
                "position": player.position,
                "profile_picture": player.profile_picture,
                "age": player.age,
                "jersey_number": player.jersey_number,
                "height": player.height,
                "weight": player.weight,
                "bio": player.bio,
                "created_at": player.created_at,
                "updated_at": player.updated_at,
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/player/{player_id}", description="Delete a player profile")
def delete_player(
    player_id: int,
    auth_user: Annotated[AuthUser, Depends(jwt_middleware)],
):
    # Only ADMIN or GUARDIAN can delete player profiles
    if not auth_user.roles or (ROLE_ADMIN not in auth_user.roles and ROLE_GUARDIAN not in auth_user.roles):
        raise HTTPException(
            status_code=403,
            detail="Access denied: Only ADMIN or GUARDIAN roles can delete a player profile."
        )

    try:
        player_service.delete(player_id)
        return {"message": "Player profile deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.get("/players/team", description="Get players by team for OFFICIAL role only")
def get_players_by_team_for_official(
    auth_user: Annotated[AuthUser, Depends(jwt_middleware)],
):
    # Only OFFICIAL role can access this endpoint
    if not auth_user.roles or ROLE_OFFICIAL not in auth_user.roles:
        raise HTTPException(
            status_code=403,
            detail="Access denied: Only OFFICIAL role can view players by team."
        )

    try:
        # Get the official ID based on the logged-in user's ID
        official = official_service.find_by_user_id(auth_user.id)
        if not official:
            raise HTTPException(
                status_code=404,
                detail="Official profile not found for the logged-in user."
            )

        # Get the team ID associated with the official
        team_official = official_service.find_team_official_by_official_id(official.id)
        if not team_official:
            raise HTTPException(
                status_code=404,
                detail="No team associated with the logged-in official."
            )

        # Fetch players by team ID
        players = player_service.find_by_team_id(team_official.team_id)
        return {
            "data": [
                {
                    "id": player.id,
                    "name": player.name,
                    "position": player.position,
                    "profile_picture": player.profile_picture,
                    "age": player.age,
                    "jersey_number": player.jersey_number,
                    "height": player.height,
                    "weight": player.weight,
                    "bio": player.bio,
                    "created_at": player.created_at,
                    "updated_at": player.updated_at,
                }
                for player in players
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
