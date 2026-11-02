"""Generic in-memory store.

Storage only: no business rule, no validation, no domain error. A lookup that
finds nothing returns `None` and the Service decides what that means.

Objects are copied in and out, so a caller mutating what it received does not
silently change what is stored. Persisting a change requires calling `update`,
which is how a real database-backed repository would behave.
"""

from typing import Generic, TypeVar

from app.models.common import Entity

T = TypeVar("T", bound=Entity)


class InMemoryRepository(Generic[T]):
    def __init__(self) -> None:
        self._items: dict[str, T] = {}

    def add(self, item: T) -> T:
        self._items[item.id] = item.model_copy(deep=True)
        return item.model_copy(deep=True)

    def get(self, item_id: str) -> T | None:
        item = self._items.get(item_id)
        return item.model_copy(deep=True) if item is not None else None

    def list(self) -> list[T]:
        return [item.model_copy(deep=True) for item in self._items.values()]

    def update(self, item: T) -> T:
        self._items[item.id] = item.model_copy(deep=True)
        return item.model_copy(deep=True)

    def delete(self, item_id: str) -> bool:
        return self._items.pop(item_id, None) is not None

    def clear(self) -> None:
        self._items.clear()

    def count(self) -> int:
        return len(self._items)
