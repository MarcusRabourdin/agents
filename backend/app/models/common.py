"""Schemas shared by every endpoint, and the base class of stored objects."""

from pydantic import BaseModel, Field


class Entity(BaseModel):
    """Anything the Repository layer can store, identified by a string id."""

    id: str


class ErrorResponse(BaseModel):
    """Body returned with every 4xx and 5xx. Matches FastAPI's own error shape."""

    detail: str = Field(examples=["game 7f3a1c2e not found"])
