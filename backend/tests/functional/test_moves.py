"""Functional tests for the move endpoints."""

from fastapi.testclient import TestClient

# 1. f3 e5 2. g4 Qh4# - the fool's mate, black mates in two.
FOOLS_MATE = ["f2f3", "e7e5", "g2g4", "d8h4"]


def play(client: TestClient, game: dict[str, str], uci: str, color: str = "white"):
    return client.post(
        f"/games/{game['id']}/moves",
        json={"player_id": game[color], "uci": uci},
    )


def test_post_game_move_advances_the_game(
    client: TestClient, game: dict[str, str]
) -> None:
    response = play(client, game, "e2e4")

    assert response.status_code == 201
    body = response.json()
    assert body["move_count"] == 1
    assert body["turn"] == "black"
    assert body["status"] == "in_progress"
    assert body["fen"].startswith("rnbqkbnr/pppppppp/8/8/4P3")


def test_post_game_move_illegal_returns_422(
    client: TestClient, game: dict[str, str]
) -> None:
    response = play(client, game, "e2e5")

    assert response.status_code == 422
    assert "not a legal move" in response.json()["detail"]


def test_post_game_move_malformed_uci_returns_422(
    client: TestClient, game: dict[str, str]
) -> None:
    response = play(client, game, "e2e9")

    assert response.status_code == 422


def test_post_game_move_out_of_turn_returns_409(
    client: TestClient, game: dict[str, str]
) -> None:
    response = play(client, game, "e7e5", color="black")

    assert response.status_code == 409
    assert "not player" in response.json()["detail"]


def test_post_game_move_by_an_outsider_returns_403(
    client: TestClient, game: dict[str, str]
) -> None:
    response = play(client, game, "e2e4", color="stranger")

    assert response.status_code == 403


def test_post_game_move_unknown_game_returns_404(
    client: TestClient, game: dict[str, str]
) -> None:
    response = client.post(
        "/games/ghost/moves",
        json={"player_id": game["white"], "uci": "e2e4"},
    )

    assert response.status_code == 404


def test_post_game_move_detects_checkmate(
    client: TestClient, game: dict[str, str]
) -> None:
    colors = ["white", "black", "white", "black"]
    for uci, color in zip(FOOLS_MATE, colors, strict=True):
        response = play(client, game, uci, color=color)
        assert response.status_code == 201, response.text

    body = response.json()
    assert body["status"] == "checkmate"
    assert body["winner"] == "black"
    assert body["is_check"] is True
    assert body["move_count"] == 4


def test_post_game_move_after_checkmate_returns_409(
    client: TestClient, game: dict[str, str]
) -> None:
    for uci, color in zip(FOOLS_MATE, ["white", "black", "white", "black"], strict=True):
        play(client, game, uci, color=color)

    response = play(client, game, "e2e4")

    assert response.status_code == 409
    assert "already over" in response.json()["detail"]


def test_get_game_moves_lists_moves_in_order(
    client: TestClient, game: dict[str, str]
) -> None:
    play(client, game, "e2e4")
    play(client, game, "e7e5", color="black")

    response = client.get(f"/games/{game['id']}/moves")

    assert response.status_code == 200
    moves = response.json()
    assert [move["number"] for move in moves] == [1, 2]
    assert [move["san"] for move in moves] == ["e4", "e5"]
    assert [move["color"] for move in moves] == ["white", "black"]


def test_get_game_moves_is_empty_on_a_new_game(
    client: TestClient, game: dict[str, str]
) -> None:
    response = client.get(f"/games/{game['id']}/moves")

    assert response.status_code == 200
    assert response.json() == []


def test_get_game_moves_unknown_game_returns_404(client: TestClient) -> None:
    response = client.get("/games/ghost/moves")

    assert response.status_code == 404
