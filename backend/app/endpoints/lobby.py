"""Matchmaking lobby endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status

from app.dependencies import get_lobby_service
from app.endpoints.docs import CONFLICT, NOT_FOUND
from app.errors import AlreadyQueuedError, PlayerNotFoundError
from app.models.lobby import QueueJoinRequest, QueueJoinResponse
from app.models.player import PlayerResponse
from app.services.lobby import LobbyService

router = APIRouter(prefix="/lobby", tags=["lobby"])


@router.get(
    "/queue",
    response_model=list[PlayerResponse],
    summary="List the players waiting for an opponent",
    response_description="The waiting players",
)
def get_lobby_queue(
    service: LobbyService = Depends(get_lobby_service),
) -> list[PlayerResponse]:
    return service.list_queue()


@router.post(
    "/queue",
    response_model=QueueJoinResponse,
    summary="Join the matchmaking queue",
    response_description=(
        "Queued. `game` is null while waiting, and holds the created game once "
        "an opponent has been matched."
    ),
    responses=NOT_FOUND | CONFLICT,
)
def post_lobby_queue(
    body: QueueJoinRequest,
    service: LobbyService = Depends(get_lobby_service),
) -> QueueJoinResponse:
    try:
        return service.join_queue(body.player_id)
    except PlayerNotFoundError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(exc)) from exc
    except AlreadyQueuedError as exc:
        raise HTTPException(status.HTTP_409_CONFLICT, str(exc)) from exc
