"""Reusable OpenAPI `responses` fragments.

Endpoints merge these with `|` so every documented error shares one body shape
and the generated `doc/swagger.yaml` stays consistent.
"""

from typing import Any

from app.models.common import ErrorResponse


def _error(description: str) -> dict[str, Any]:
    return {"model": ErrorResponse, "description": description}


NOT_FOUND = {404: _error("Resource does not exist")}
FORBIDDEN = {403: _error("Caller is not a player of this game")}
CONFLICT = {409: _error("The current state does not allow this action")}
UNPROCESSABLE = {422: _error("Malformed request body")}
ILLEGAL_MOVE = {422: _error("Illegal move for the current position")}
TURN_CONFLICT = {409: _error("Not this player's turn, or the game is already over")}
