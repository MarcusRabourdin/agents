"""Application settings."""

import os

API_TITLE = "Online Chess Platform API"
API_VERSION = "0.1.0"
API_DESCRIPTION = (
    "REST API of the online chess platform. Layering is "
    "Model -> Repository -> Service -> Endpoint, see AGENTS.md. "
    "Storage is in-memory: every object is lost on restart."
)

SERVERS = [
    {"url": "http://127.0.0.1:8000", "description": "Local development"},
]

TAGS_METADATA = [
    {"name": "players", "description": "Player accounts and ratings"},
    {"name": "games", "description": "Game lifecycle and board state"},
    {"name": "moves", "description": "Playing and listing moves"},
    {"name": "lobby", "description": "Matchmaking queue"},
]

# Origins allowed to call the API. The Vite dev server by default.
CORS_ORIGINS = os.environ.get(
    "CHESS_CORS_ORIGINS",
    "http://localhost:5173,http://127.0.0.1:5173",
).split(",")
