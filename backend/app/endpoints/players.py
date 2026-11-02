"""Player endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status

from app.dependencies import get_player_service
from app.endpoints.docs import CONFLICT, NOT_FOUND, UNPROCESSABLE
from app.errors import PlayerNotFoundError, UsernameAlreadyTakenError
from app.models.player import PlayerCreateRequest, PlayerResponse
from app.services.player import PlayerService

router = APIRouter(prefix="/players", tags=["players"])


@router.post(
    "",
    response_model=PlayerResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a player",
    response_description="Player created",
    responses=CONFLICT | UNPROCESSABLE,
)
def post_player(
    body: PlayerCreateRequest,
    service: PlayerService = Depends(get_player_service),
) -> PlayerResponse:
    try:
        return service.create_player(body.username)
    except UsernameAlreadyTakenError as exc:
        raise HTTPException(status.HTTP_409_CONFLICT, str(exc)) from exc


@router.get(
    "/{player_id}",
    response_model=PlayerResponse,
    summary="Get a player",
    response_description="The player",
    responses=NOT_FOUND,
)
def get_player(
    player_id: str,
    service: PlayerService = Depends(get_player_service),
) -> PlayerResponse:
    try:
        return service.get_player(player_id)
    except PlayerNotFoundError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(exc)) from exc
