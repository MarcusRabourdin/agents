"""Player storage."""

from app.models.player import Player
from app.repositories.base import InMemoryRepository


class PlayerRepository(InMemoryRepository[Player]):
    def find_by_username(self, username: str) -> Player | None:
        for player in self._items.values():
            if player.username == username:
                return player.model_copy(deep=True)
        return None
