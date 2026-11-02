"""Move endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status

from app.dependencies import get_game_service
from app.endpoints.docs import FORBIDDEN, ILLEGAL_MOVE, NOT_FOUND, TURN_CONFLICT
from app.errors import (
    GameAlreadyOverError,
    GameNotFoundError,
    IllegalMoveError,
    NotAPlayerOfGameError,
    NotPlayerTurnError,
)
from app.models.game import (
    GameStateResponse,
    LegalMovesResponse,
    MoveRequest,
    MoveResponse,
)
from app.services.game import GameService

router = APIRouter(prefix="/games", tags=["moves"])


@router.get(
    "/{game_id}/moves",
    response_model=list[MoveResponse],
    summary="List the moves played in a game",
    response_description="The moves, in playing order",
    responses=NOT_FOUND,
)
def get_game_moves(
    game_id: str,
    service: GameService = Depends(get_game_service),
) -> list[MoveResponse]:
    try:
        return service.list_moves(game_id)
    except GameNotFoundError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(exc)) from exc


@router.get(
    "/{game_id}/legal-moves",
    response_model=LegalMovesResponse,
    summary="List every legal move in the current position",
    response_description="The legal moves, with the position they come from",
    responses=NOT_FOUND,
)
def get_game_legal_moves(
    game_id: str,
    service: GameService = Depends(get_game_service),
) -> LegalMovesResponse:
    try:
        return service.list_legal_moves(game_id)
    except GameNotFoundError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(exc)) from exc


@router.post(
    "/{game_id}/moves",
    response_model=GameStateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Play a move",
    response_description="Move accepted, new game state returned",
    responses=FORBIDDEN | NOT_FOUND | TURN_CONFLICT | ILLEGAL_MOVE,
)
def post_game_move(
    game_id: str,
    body: MoveRequest,
    service: GameService = Depends(get_game_service),
) -> GameStateResponse:
    try:
        return service.play_move(game_id, body.player_id, body.uci)
    except GameNotFoundError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(exc)) from exc
    except NotAPlayerOfGameError as exc:
        raise HTTPException(status.HTTP_403_FORBIDDEN, str(exc)) from exc
    except (NotPlayerTurnError, GameAlreadyOverError) as exc:
        raise HTTPException(status.HTTP_409_CONFLICT, str(exc)) from exc
    except IllegalMoveError as exc:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, str(exc)) from exc
