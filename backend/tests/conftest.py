"""Shared fixtures.

Every store is emptied around each test, so no state leaks between cases.
"""

from collections.abc import Callable, Iterator

import pytest
from fastapi.testclient import TestClient

from app.dependencies import reset_state
from app.main import app


@pytest.fixture(autouse=True)
def clean_state() -> Iterator[None]:
    reset_state()
    yield
    reset_state()


@pytest.fixture
def client() -> Iterator[TestClient]:
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def make_player(client: TestClient) -> Callable[[str], str]:
    def _make_player(username: str) -> str:
        response = client.post("/players", json={"username": username})
        assert response.status_code == 201, response.text
        return response.json()["id"]

    return _make_player


@pytest.fixture
def game(client: TestClient, make_player: Callable[[str], str]) -> dict[str, str]:
    """A running game plus the ids of its two players and an outsider."""
    white = make_player("white_side")
    black = make_player("black_side")
    stranger = make_player("stranger")
    response = client.post(
        "/games",
        json={"white_player_id": white, "black_player_id": black},
    )
    assert response.status_code == 201, response.text
    return {
        "id": response.json()["id"],
        "white": white,
        "black": black,
        "stranger": stranger,
    }
