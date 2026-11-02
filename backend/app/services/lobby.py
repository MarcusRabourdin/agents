"""Matchmaking business logic.

The queue is a FIFO: the player who has been waiting longest is matched first
and gets white.
"""

from app.errors import AlreadyQueuedError
from app.models.lobby import QueueJoinResponse
from app.models.player import PlayerResponse
from app.repositories.lobby import MatchmakingQueueRepository
from app.services.game import GameService
from app.services.player import PlayerService


class LobbyService:
    def __init__(
        self,
        queue: MatchmakingQueueRepository,
        players: PlayerService,
        games: GameService,
    ) -> None:
        self._queue = queue
        self._players = players
        self._games = games

    def list_queue(self) -> list[PlayerResponse]:
        return [self._players.get_player(player_id) for player_id in self._queue.list()]

    def join_queue(self, player_id: str) -> QueueJoinResponse:
        """Queue a player, pairing them with whoever has waited longest.

        Returns `queued=True` with no game while nobody else is waiting, and
        `queued=False` with the created game once an opponent was found.
        """
        self._players.require_player(player_id)
        if self._queue.contains(player_id):
            raise AlreadyQueuedError(player_id)

        opponent_id = self._queue.pop_first()
        if opponent_id is None:
            self._queue.add(player_id)
            return QueueJoinResponse(queued=True, game=None)

        game = self._games.create_game(
            white_player_id=opponent_id,
            black_player_id=player_id,
        )
        return QueueJoinResponse(queued=False, game=game)

    def leave_queue(self, player_id: str) -> bool:
        return self._queue.remove(player_id)
