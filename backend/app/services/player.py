"""Player business logic."""

from uuid import uuid4

from app.errors import PlayerNotFoundError, UsernameAlreadyTakenError
from app.models.player import Player, PlayerResponse
from app.repositories.player import PlayerRepository


class PlayerService:
    def __init__(self, players: PlayerRepository) -> None:
        self._players = players

    def create_player(self, username: str) -> PlayerResponse:
        """Create a player. A username is unique across the platform."""
        if self._players.find_by_username(username) is not None:
            raise UsernameAlreadyTakenError(username)
        player = Player(id=str(uuid4()), username=username)
        return PlayerResponse.from_player(self._players.add(player))

    def get_player(self, player_id: str) -> PlayerResponse:
        return PlayerResponse.from_player(self.require_player(player_id))

    def require_player(self, player_id: str) -> Player:
        """Return the stored player or raise. Used by the other services."""
        player = self._players.get(player_id)
        if player is None:
            raise PlayerNotFoundError(player_id)
        return player
