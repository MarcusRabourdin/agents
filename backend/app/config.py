"""Application settings."""

import os

API_TITLE = "Online Chess Platform API"
API_VERSION = "0.1.0"
API_DESCRIPTION = (
    "REST API of the online chess platform. Layering is "
    "Model -> Repository -> Service -> Endpoint, see AGENTS.md. "
    "Storage is in-memory: every object is lost on restart."
)

# Where Swagger UI at /docs sends its "Try it out" requests. The default is a
# plain `uvicorn` run, and doc/swagger.yaml is generated from it, so changing it
# here means regenerating the committed spec.
#
# ./launch overrides it with "/", relative to whatever origin served the docs
# page: that script can put the API on another port or bind it for the LAN, and
# a hardcoded 127.0.0.1:8000 would then aim every request from /docs at a port
# nothing is listening on.
API_SERVER_URL = os.environ.get("CHESS_API_URL", "http://127.0.0.1:8000")

SERVERS = [
    {"url": API_SERVER_URL, "description": "Local development"},
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
