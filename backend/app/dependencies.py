"""Dependency injection wiring.

The repositories are process-wide singletons because storage is in-memory. The
services are built per request from them, which keeps them cheap to fake in a
unit test. Endpoints only ever ask for a service.
"""

from fastapi import Depends

from app.repositories.game import GameRepository
from app.repositories.lobby import MatchmakingQueueRepository
from app.repositories.player import PlayerRepository
from app.services.game import GameService
from app.services.lobby import LobbyService
from app.services.player import PlayerService

_player_repository = PlayerRepository()
_game_repository = GameRepository()
_queue_repository = MatchmakingQueueRepository()


def get_player_repository() -> PlayerRepository:
    return _player_repository


def get_game_repository() -> GameRepository:
    return _game_repository


def get_queue_repository() -> MatchmakingQueueRepository:
    return _queue_repository


def get_player_service(
    players: PlayerRepository = Depends(get_player_repository),
) -> PlayerService:
    return PlayerService(players)


def get_game_service(
    games: GameRepository = Depends(get_game_repository),
    players: PlayerService = Depends(get_player_service),
) -> GameService:
    return GameService(games, players)


def get_lobby_service(
    queue: MatchmakingQueueRepository = Depends(get_queue_repository),
    players: PlayerService = Depends(get_player_service),
    games: GameService = Depends(get_game_service),
) -> LobbyService:
    return LobbyService(queue, players, games)


def reset_state() -> None:
    """Empty every store. Used by the test suite between cases."""
    _player_repository.clear()
    _game_repository.clear()
    _queue_repository.clear()
