"""Functional tests for the matchmaking lobby endpoints."""

from collections.abc import Callable

from fastapi.testclient import TestClient


def test_post_lobby_queue_first_player_waits(
    client: TestClient, make_player: Callable[[str], str]
) -> None:
    player = make_player("first_in")

    response = client.post("/lobby/queue", json={"player_id": player})

    assert response.status_code == 200
    assert response.json() == {"queued": True, "game": None}


def test_post_lobby_queue_second_player_gets_a_game(
    client: TestClient, make_player: Callable[[str], str]
) -> None:
    first = make_player("first_in")
    second = make_player("second_in")
    client.post("/lobby/queue", json={"player_id": first})

    response = client.post("/lobby/queue", json={"player_id": second})

    assert response.status_code == 200
    body = response.json()
    assert body["queued"] is False
    assert body["game"] is not None
    assert body["game"]["white_player_id"] == first
    assert body["game"]["black_player_id"] == second
    assert body["game"]["status"] == "in_progress"


def test_post_lobby_queue_empties_the_queue_once_matched(
    client: TestClient, make_player: Callable[[str], str]
) -> None:
    first = make_player("first_in")
    second = make_player("second_in")
    client.post("/lobby/queue", json={"player_id": first})
    client.post("/lobby/queue", json={"player_id": second})

    assert client.get("/lobby/queue").json() == []


def test_post_lobby_queue_twice_returns_409(
    client: TestClient, make_player: Callable[[str], str]
) -> None:
    player = make_player("first_in")
    client.post("/lobby/queue", json={"player_id": player})

    response = client.post("/lobby/queue", json={"player_id": player})

    assert response.status_code == 409
    assert "already in the queue" in response.json()["detail"]


def test_post_lobby_queue_unknown_player_returns_404(client: TestClient) -> None:
    response = client.post("/lobby/queue", json={"player_id": "ghost"})

    assert response.status_code == 404


def test_get_lobby_queue_lists_waiting_players(
    client: TestClient, make_player: Callable[[str], str]
) -> None:
    player = make_player("first_in")
    client.post("/lobby/queue", json={"player_id": player})

    response = client.get("/lobby/queue")

    assert response.status_code == 200
    assert [entry["username"] for entry in response.json()] == ["first_in"]


def test_get_lobby_queue_is_empty_by_default(client: TestClient) -> None:
    response = client.get("/lobby/queue")

    assert response.status_code == 200
    assert response.json() == []
