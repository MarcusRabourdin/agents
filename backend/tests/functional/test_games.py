"""Functional tests for the game lifecycle endpoints."""

from collections.abc import Callable

from fastapi.testclient import TestClient

STARTING_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"


def test_post_game_starts_in_progress_with_white_to_move(
    client: TestClient, make_player: Callable[[str], str]
) -> None:
    white = make_player("white_side")
    black = make_player("black_side")

    response = client.post(
        "/games",
        json={"white_player_id": white, "black_player_id": black},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "in_progress"
    assert body["turn"] == "white"
    assert body["fen"] == STARTING_FEN
    assert body["winner"] is None
    assert body["is_check"] is False
    assert body["move_count"] == 0


def test_post_game_unknown_player_returns_404(
    client: TestClient, make_player: Callable[[str], str]
) -> None:
    white = make_player("white_side")

    response = client.post(
        "/games",
        json={"white_player_id": white, "black_player_id": "ghost"},
    )

    assert response.status_code == 404


def test_post_game_against_self_returns_422(
    client: TestClient, make_player: Callable[[str], str]
) -> None:
    player = make_player("lonely_one")

    response = client.post(
        "/games",
        json={"white_player_id": player, "black_player_id": player},
    )

    assert response.status_code == 422
    assert "themselves" in response.json()["detail"]


def test_get_game_returns_current_state(
    client: TestClient, game: dict[str, str]
) -> None:
    response = client.get(f"/games/{game['id']}")

    assert response.status_code == 200
    assert response.json()["id"] == game["id"]
    assert response.json()["white_player_id"] == game["white"]


def test_get_game_unknown_returns_404(client: TestClient) -> None:
    response = client.get("/games/does-not-exist")

    assert response.status_code == 404


def test_get_games_lists_every_game(client: TestClient, game: dict[str, str]) -> None:
    response = client.get("/games")

    assert response.status_code == 200
    assert [entry["id"] for entry in response.json()] == [game["id"]]


def test_get_games_filters_on_status(client: TestClient, game: dict[str, str]) -> None:
    client.post(f"/games/{game['id']}/resign", json={"player_id": game["white"]})

    assert client.get("/games", params={"status": "in_progress"}).json() == []
    resigned = client.get("/games", params={"status": "resigned"}).json()
    assert [entry["id"] for entry in resigned] == [game["id"]]


def test_get_games_rejects_unknown_status(client: TestClient) -> None:
    response = client.get("/games", params={"status": "flying"})

    assert response.status_code == 422


def test_post_game_resign_gives_the_win_to_the_opponent(
    client: TestClient, game: dict[str, str]
) -> None:
    response = client.post(
        f"/games/{game['id']}/resign",
        json={"player_id": game["white"]},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "resigned"
    assert body["winner"] == "black"


def test_post_game_resign_by_an_outsider_returns_403(
    client: TestClient, game: dict[str, str]
) -> None:
    response = client.post(
        f"/games/{game['id']}/resign",
        json={"player_id": game["stranger"]},
    )

    assert response.status_code == 403
    assert "not a player" in response.json()["detail"]


def test_post_game_resign_twice_returns_409(
    client: TestClient, game: dict[str, str]
) -> None:
    client.post(f"/games/{game['id']}/resign", json={"player_id": game["white"]})

    response = client.post(
        f"/games/{game['id']}/resign",
        json={"player_id": game["black"]},
    )

    assert response.status_code == 409
    assert "already over" in response.json()["detail"]


def test_post_game_resign_unknown_game_returns_404(
    client: TestClient, make_player: Callable[[str], str]
) -> None:
    player = make_player("marcus")

    response = client.post("/games/ghost/resign", json={"player_id": player})

    assert response.status_code == 404
