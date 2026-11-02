"""Player models: the domain object and its request/response schemas."""

from pydantic import BaseModel, Field

from app.models.common import Entity

STARTING_RATING = 1200


class Player(Entity):
    """A player account, as stored by the Repository layer."""

    username: str
    rating: int = STARTING_RATING


class PlayerCreateRequest(BaseModel):
    username: str = Field(min_length=3, max_length=32, examples=["marcus"])


class PlayerResponse(BaseModel):
    id: str
    username: str = Field(examples=["marcus"])
    rating: int = Field(description="Elo rating, 1200 on creation", examples=[1200])

    @classmethod
    def from_player(cls, player: Player) -> "PlayerResponse":
        return cls(id=player.id, username=player.username, rating=player.rating)
