"""Unit tests for the storage layer."""

from app.models.game import Game, GameStatus
from app.models.player import Player
from app.repositories.game import GameRepository
from app.repositories.lobby import MatchmakingQueueRepository
from app.repositories.player import PlayerRepository


def a_game(game_id: str, status: GameStatus = GameStatus.IN_PROGRESS) -> Game:
    return Game(
        id=game_id,
        white_player_id="white",
        black_player_id="black",
        status=status,
    )


def test_get_returns_a_copy_so_the_store_cannot_be_mutated_by_accident() -> None:
    repo = GameRepository()
    repo.add(a_game("g1"))

    escaped = repo.get("g1")
    assert escaped is not None
    escaped.status = GameStatus.RESIGNED

    stored = repo.get("g1")
    assert stored is not None
    assert stored.status is GameStatus.IN_PROGRESS


def test_update_persists_the_change() -> None:
    repo = GameRepository()
    repo.add(a_game("g1"))

    game = repo.get("g1")
    assert game is not None
    game.status = GameStatus.DRAW
    repo.update(game)

    stored = repo.get("g1")
    assert stored is not None
    assert stored.status is GameStatus.DRAW


def test_get_unknown_returns_none_rather_than_raising() -> None:
    assert GameRepository().get("ghost") is None


def test_delete_and_clear() -> None:
    repo = GameRepository()
    repo.add(a_game("g1"))
    repo.add(a_game("g2"))

    assert repo.delete("g1") is True
    assert repo.delete("g1") is False
    assert repo.count() == 1

    repo.clear()
    assert repo.count() == 0


def test_list_by_status_and_by_player() -> None:
    repo = GameRepository()
    repo.add(a_game("g1"))
    repo.add(a_game("g2", status=GameStatus.RESIGNED))

    assert [game.id for game in repo.list_by_status(GameStatus.RESIGNED)] == ["g2"]
    assert len(repo.list_by_player("white")) == 2
    assert repo.list_by_player("ghost") == []


def test_find_by_username() -> None:
    repo = PlayerRepository()
    repo.add(Player(id="p1", username="marcus"))

    found = repo.find_by_username("marcus")
    assert found is not None
    assert found.id == "p1"
    assert repo.find_by_username("nobody") is None


def test_queue_is_first_in_first_out() -> None:
    queue = MatchmakingQueueRepository()
    queue.add("p1")
    queue.add("p2")

    assert queue.contains("p1") is True
    assert queue.list() == ["p1", "p2"]
    assert queue.pop_first() == "p1"
    assert queue.pop_first() == "p2"
    assert queue.pop_first() is None


def test_queue_remove_and_clear() -> None:
    queue = MatchmakingQueueRepository()
    queue.add("p1")

    assert queue.remove("p1") is True
    assert queue.remove("p1") is False

    queue.add("p2")
    queue.clear()
    assert queue.list() == []
