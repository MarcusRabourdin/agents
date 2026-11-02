"""Functional tests for the player endpoints."""

from collections.abc import Callable

from fastapi.testclient import TestClient


def test_post_player_creates_player_with_starting_rating(client: TestClient) -> None:
    response = client.post("/players", json={"username": "marcus"})

    assert response.status_code == 201
    body = response.json()
    assert body["username"] == "marcus"
    assert body["rating"] == 1200
    assert body["id"]


def test_post_player_rejects_duplicate_username(client: TestClient) -> None:
    client.post("/players", json={"username": "marcus"})

    response = client.post("/players", json={"username": "marcus"})

    assert response.status_code == 409
    assert "already taken" in response.json()["detail"]


def test_post_player_rejects_too_short_username(client: TestClient) -> None:
    response = client.post("/players", json={"username": "ab"})

    assert response.status_code == 422


def test_post_player_rejects_missing_username(client: TestClient) -> None:
    response = client.post("/players", json={})

    assert response.status_code == 422


def test_get_player_returns_the_player(
    client: TestClient, make_player: Callable[[str], str]
) -> None:
    player_id = make_player("marcus")

    response = client.get(f"/players/{player_id}")

    assert response.status_code == 200
    assert response.json() == {"id": player_id, "username": "marcus", "rating": 1200}


def test_get_player_unknown_returns_404(client: TestClient) -> None:
    response = client.get("/players/does-not-exist")

    assert response.status_code == 404
    assert "not found" in response.json()["detail"]
