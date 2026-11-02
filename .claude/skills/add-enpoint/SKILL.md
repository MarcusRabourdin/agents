---
name: add-enpoint
description: >
  Give the full process to follows when creating/modificating an enpoint.
  Use this skill whenever the user asks to create or to modify and enpoint.
  Covers the FastAPI layering of this project: Model -> Repository -> Service -> Endpoint.
---

# Enpoint Conventional Procedure

## When to Activate

Activate this skill when:
  - The user asks you to create and enpoint
  - The user asks you to modify and enpoint
  - You are about to create/modify an endpoint
  - The user asks a question about endpoint

## The Layers

```
Endpoint   app/endpoints/<aggregate>.py       HTTP only
    |
Service    app/services/<aggregate>.py        all the logic
    |
Repository app/repositories/<aggregate>.py    storage only
    |
Model      app/models/<aggregate>.py          Pydantic objects
```

A layer imports only the layer directly below it. Never upward, never skipping.

## Name Format

The handler function name must start with the HTTP method, followed by a short
name describing the resource. Python naming applies, so `snake_case`:

```
<method>_<short_name>(<typed args>) -> <ResponseModel>
```

### Examples

Good:
- `get_lobby_chat(lobby_id: int) -> ChatResponse`
- `post_lobby_message(lobby_id: int, body: MessageRequest) -> MessageResponse`
- `get_player_rating(player_id: str) -> RatingResponse`
- `post_game_move(game_id: str, body: MoveRequest) -> GameStateResponse`

Bad:
- `player_rating()` - no method specified
- `getLobbyChat(lobby_id)` - camelCase, this is Python
- `post_message(player_id)` - short name must say which resource
- `get_game(game_id)` with no return annotation - type hints are mandatory

### Route and router

- Path is plural, kebab-case, lowercase: `/games/{game_id}/moves`.
- Path parameter names match the function argument names exactly.
- One `APIRouter` per aggregate, declared at the top of the module:
  `router = APIRouter(prefix="/games", tags=["games"])`.
- The router is registered once in `app/main.py` with `app.include_router(...)`.

## Rules

1. Always follow the format of the other endpoints.
2. An endpoint MUST only handle the reception of the API call and return a
   response object. Parse, delegate to the Service, return.
3. An endpoint does not make any logic check, that's the Service layer job. No
   `if` on business state, no turn check, no legality check, no ownership check.
4. An endpoint does not modify the storage, that's the Repository layer job. An
   endpoint never imports a repository.
5. The Service is obtained through dependency injection only:
   `service: GameService = Depends(get_game_service)`. Never instantiate a
   Service or a Repository inside an endpoint.
6. Every endpoint declares an explicit `response_model` and an explicit
   `status_code` when it is not 200.
7. Request bodies are Pydantic models. Never `dict`, never `Any`.
8. The Service raises domain errors from `app/errors.py`. The endpoint is the
   only layer allowed to translate them into `HTTPException`. The Service never
   raises `HTTPException`.
9. No bare `except:`. Catch the specific domain errors, then a final
   `except Exception` mapping to 500 if the endpoint needs a safety net.
10. Type hints on every parameter and on the return value.

## Endpoint Shape

```python
from fastapi import APIRouter, Depends, HTTPException, status

from app.dependencies import get_game_service
from app.errors import GameNotFoundError, IllegalMoveError, NotPlayerTurnError
from app.models.game import GameStateResponse, MoveRequest
from app.services.game import GameService

router = APIRouter(prefix="/games", tags=["games"])


@router.post(
    "/{game_id}/moves",
    response_model=GameStateResponse,
    status_code=status.HTTP_201_CREATED,
)
def post_game_move(
    game_id: str,
    body: MoveRequest,
    service: GameService = Depends(get_game_service),
) -> GameStateResponse:
    try:
        return service.play_move(game_id, body.player_id, body.uci)
    except GameNotFoundError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(exc)) from exc
    except NotPlayerTurnError as exc:
        raise HTTPException(status.HTTP_409_CONFLICT, str(exc)) from exc
    except IllegalMoveError as exc:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, str(exc)) from exc
```

Reusable `responses=` fragments for the error bodies live in
`app/endpoints/docs.py`. Merge them with `|` instead of writing the dict inline.

## Status Code Mapping

| Situation | Code |
|-----------|------|
| Read succeeded | 200 |
| Resource created | 201 |
| Deleted, nothing to return | 204 |
| Malformed body or bad types | 422 (FastAPI does it for you) |
| Business rule rejected the input (illegal move) | 422 |
| Caller is not allowed (not their game) | 403 |
| Resource does not exist | 404 |
| State conflict (not your turn, game already over) | 409 |
| Unexpected failure | 500 |

## Process

1. Before writing code, read carefully the other endpoints in `app/endpoints/`.
2. Read the other layers' functions: the Service, the Repository and the Models
   for the aggregate you are touching. Reuse what exists before adding anything.
3. Build the endpoint using a try/except, following the shape above.
4. If the necessary function(s) do/does not exist in the other layers, implement
   them using vertical slices: add only what this endpoint needs, bottom-up.
   - Model: the request/response schemas and any new domain field.
   - Repository: the storage accessor, no logic.
   - Service: the rule, raising a domain error from `app/errors.py`.
   - Endpoint: the handler.
   - Register the router in `app/main.py` if the aggregate is new.
   - Add the DI provider in `app/dependencies.py` if the Service is new.
5. Add tests. Functional tests are mandatory for each endpoint you add or
   change; unitary tests are optional but encouraged for new Service rules.
   - Functional tests live in `backend/tests/functional/test_<aggregate>.py` and
     go through `TestClient`.
   - Cover the happy path plus every status code listed in the mapping that this
     endpoint can return.
6. Run the full test suite to check for any regression. If there is any, fix the
   code and re-run. Do it while any test still fails.

   ```sh
   .venv/bin/python -m pytest backend/tests
   ```
7. Run the new tests, check for any errors. If there is any, fix the code and
   re-run the new tests. Do it while any test still fails.

   ```sh
   .venv/bin/python -m pytest backend/tests/functional/test_<aggregate>.py -v
   ```
8. Regenerate `doc/swagger.yaml`. It is the contract the frontend is written
   against, so it must never drift from the code.

   ```sh
   .venv/bin/python backend/scripts/export_swagger.py
   ```

   Never hand-edit that file. What you want documented goes in the route
   decorator (`summary`, `response_description`, `responses=`) and in the model
   fields (`Field(description=..., examples=[...])`), then you regenerate.

   Then read the diff. Check the new path is there, that every status code the
   endpoint can return is documented, and that nothing else moved.

## Self-Check Before Declaring Done

  - [ ] Handler name is `<method>_<short_name>`, snake_case
  - [ ] Fully type hinted, explicit `response_model`
  - [ ] No `if` on business state in the endpoint
  - [ ] No repository import in the endpoint
  - [ ] Service injected with `Depends`, not constructed
  - [ ] Every domain error mapped to a status code
  - [ ] Functional tests written and passing
  - [ ] Full suite passing
  - [ ] `doc/swagger.yaml` updated, `operationId` matches the handler name
