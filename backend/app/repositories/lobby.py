"""Matchmaking queue storage.

A plain FIFO of player ids. Storage only: it does not decide who plays whom.
"""


class MatchmakingQueueRepository:
    def __init__(self) -> None:
        self._waiting: list[str] = []

    def add(self, player_id: str) -> None:
        self._waiting.append(player_id)

    def contains(self, player_id: str) -> bool:
        return player_id in self._waiting

    def list(self) -> list[str]:
        return list(self._waiting)

    def pop_first(self) -> str | None:
        return self._waiting.pop(0) if self._waiting else None

    def remove(self, player_id: str) -> bool:
        if player_id in self._waiting:
            self._waiting.remove(player_id)
            return True
        return False

    def clear(self) -> None:
        self._waiting.clear()
