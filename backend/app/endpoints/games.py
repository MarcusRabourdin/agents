"""Game lifecycle endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.dependencies import get_game_service
from app.endpoints.docs import CONFLICT, FORBIDDEN, NOT_FOUND, UNPROCESSABLE
from app.errors import (
    CannotPlayAgainstSelfError,
    GameAlreadyOverError,
    GameNotFoundError,
    NotAPlayerOfGameError,
    PlayerNotFoundError,
)
from app.models.game import (
    GameCreateRequest,
    GameStateResponse,
    GameStatus,
    ResignRequest,
)
from app.services.game import GameService

router = APIRouter(prefix="/games", tags=["games"])


@router.get(
    "",
    response_model=list[GameStateResponse],
    summary="List games",
    response_description="The games",
)
def get_games(
    status_filter: GameStatus | None = Query(
        default=None,
        alias="status",
        description="Filter on game status",
    ),
    service: GameService = Depends(get_game_service),
) -> list[GameStateResponse]:
    return service.list_games(status_filter)


@router.post(
    "",
    response_model=GameStateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a game between two players",
    response_description="Game created, white to move",
    responses=NOT_FOUND | UNPROCESSABLE,
)
def post_game(
    body: GameCreateRequest,
    service: GameService = Depends(get_game_service),
) -> GameStateResponse:
    try:
        return service.create_game(body.white_player_id, body.black_player_id)
    except PlayerNotFoundError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(exc)) from exc
    except CannotPlayAgainstSelfError as exc:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, str(exc)) from exc


@router.get(
    "/{game_id}",
    response_model=GameStateResponse,
    summary="Get the current state of a game",
    response_description="The game state",
    responses=NOT_FOUND,
)
def get_game(
    game_id: str,
    service: GameService = Depends(get_game_service),
) -> GameStateResponse:
    try:
        return service.get_game(game_id)
    except GameNotFoundError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(exc)) from exc


@router.post(
    "/{game_id}/resign",
    response_model=GameStateResponse,
    summary="Resign a game",
    response_description="Game is over, the opponent wins",
    responses=FORBIDDEN | NOT_FOUND | CONFLICT,
)
def post_game_resign(
    game_id: str,
    body: ResignRequest,
    service: GameService = Depends(get_game_service),
) -> GameStateResponse:
    try:
        return service.resign(game_id, body.player_id)
    except GameNotFoundError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(exc)) from exc
    except NotAPlayerOfGameError as exc:
        raise HTTPException(status.HTTP_403_FORBIDDEN, str(exc)) from exc
    except GameAlreadyOverError as exc:
        raise HTTPException(status.HTTP_409_CONFLICT, str(exc)) from exc
