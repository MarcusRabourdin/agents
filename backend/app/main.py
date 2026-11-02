"""FastAPI application: settings, middleware and router registration only.

No business logic lives here.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.routing import APIRoute

from app.config import (
    API_DESCRIPTION,
    API_TITLE,
    API_VERSION,
    CORS_ORIGINS,
    SERVERS,
    TAGS_METADATA,
)
from app.endpoints import games, lobby, moves, players


def _operation_id(route: APIRoute) -> str:
    """Make the OpenAPI operationId the handler name, as AGENTS.md requires."""
    return route.name


app = FastAPI(
    title=API_TITLE,
    version=API_VERSION,
    description=API_DESCRIPTION,
    servers=SERVERS,
    openapi_tags=TAGS_METADATA,
    generate_unique_id_function=_operation_id,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(players.router)
app.include_router(games.router)
app.include_router(moves.router)
app.include_router(lobby.router)
