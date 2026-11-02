"""Game storage."""

from app.models.game import Game, GameStatus
from app.repositories.base import InMemoryRepository


class GameRepository(InMemoryRepository[Game]):
    def list_by_status(self, status: GameStatus) -> list[Game]:
        return [
            game.model_copy(deep=True)
            for game in self._items.values()
            if game.status == status
        ]

    def list_by_player(self, player_id: str) -> list[Game]:
        return [
            game.model_copy(deep=True)
            for game in self._items.values()
            if player_id in (game.white_player_id, game.black_player_id)
        ]
