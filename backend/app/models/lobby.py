"""Matchmaking lobby schemas."""

from pydantic import BaseModel, Field

from app.models.game import GameStateResponse


class QueueJoinRequest(BaseModel):
    player_id: str


class QueueJoinResponse(BaseModel):
    queued: bool = Field(description="True while still waiting for an opponent")
    game: GameStateResponse | None = Field(
        default=None,
        description="Null while waiting, the created game once matched",
    )
