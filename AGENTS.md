# AGENTS.md

## Project
  - The project is fullly maintain by AI/Agents
  - The project is about creating an online chess plateform
  - The webApp/Frontend is using React + Typescript + Vite.
  - The server side is using Python3

## Server stack
  - **FastAPI** - the REST framework. Chosen because it maps directly onto the
    layered architecture below: Pydantic models are the Models layer, `APIRouter`
    is the Endpoint layer, and `Depends()` injects Services without an Endpoint
    ever touching a Repository.
  - **Pydantic v2** - request/response schemas and domain object validation.
  - **Uvicorn** - ASGI server used to run the app.
  - **python-chess** - move generation, legality and FEN/PGN handling. The
    Services layer delegates all chess rules to it. Never re-implement chess
    rules by hand.
  - **pytest** + **httpx** - test runner and HTTP client used by FastAPI's
    `TestClient` for functional tests.
  - **PyYAML** - used by the export script to dump the generated schema into
    `doc/swagger.yaml`.

Storage is **in-memory only** for now (plain dicts behind the Repository layer).
No database, no ORM. Swapping in a real database later must only require
rewriting the Repository layer.

## Architecture

Four layers, strict one-way dependencies. A layer may only import the layer
directly below it:

```
Endpoint   (app/endpoints/)      HTTP only: parse, delegate, return a response
    |
Service    (app/services/)       All business logic, rules, validation
    |
Repository (app/repositories/)   Storage only: get / list / add / update / delete
    |
Model      (app/models/)         Pydantic objects, no behaviour beyond validation
```

Rules that are never broken:
  - An **Endpoint** does no logic and never touches a Repository.
  - A **Service** does no HTTP: it never raises `HTTPException`, never reads a
    `Request`, never returns a status code. It raises domain errors from
    `app/errors.py`.
  - A **Repository** does no logic: no legality check, no turn check, no
    business rule. It stores and retrieves Models.
  - A **Model** has no storage access and no business logic.
  - Nothing imports upward. If a Service needs something from an Endpoint, the
    design is wrong.
  - Composition *within* the Service layer is allowed and preferred over
    reaching down two layers: `LobbyService` uses `GameService` to open a game
    rather than touching `GameRepository`. One direction only, never a cycle.
  - Repositories hand out deep copies and persist only on `update()`, so a
    Service mutating what it read changes nothing until it saves. Treat them
    like a real database.

## Directory layout

```
backend/
  app/
    main.py              FastAPI app, middleware, router registration
    config.py            Title, version, servers, tag descriptions, CORS
    errors.py            Domain exceptions (IllegalMoveError, GameNotFoundError...)
    dependencies.py      DI providers + reset_state() for the tests
    models/              common.py (Entity, ErrorResponse), player, game, lobby
    repositories/        base.py (InMemoryRepository[T]), player, game, lobby
    services/            player, game (chess rules), lobby (matchmaking)
    endpoints/           One APIRouter per resource + docs.py (responses=)
  scripts/
    export_swagger.py    Regenerates doc/swagger.yaml, --check for CI
  tests/
    conftest.py          client, make_player and game fixtures, state reset
    unit/                Per-layer tests, dependencies built by hand
    functional/          Through the HTTP layer with TestClient
  pytest.ini
  requirements.txt
doc/
  swagger.yaml           Generated OpenAPI spec, committed, never hand-edited
frontend/                React + Typescript + Vite
flake.nix                Pinned toolchain: devShell, nix run, nix flake check
flake.lock               Pinned nixpkgs, committed
```

Aggregates: `player`, `game` (which owns moves) and `lobby`. Moves get their own
router in `endpoints/moves.py` because they are a sub-resource of a game, but
they are served by `GameService`: a move has no life of its own.

## Setup commands

Nix is the primary path. `flake.nix` pins the interpreter, every Python
library, Node and ruff, so the toolchain is identical everywhere.

```sh
nix develop                 # dev shell: python + deps, node, ruff
nix run .#                  # serve the API with --reload, from the repo root
nix flake check             # build the env and run the whole test suite
nix fmt                     # format the nix files
```

Inside `nix develop`, commands are plain:

```sh
uvicorn app.main:app --reload --app-dir backend   # http://127.0.0.1:8000, docs at /docs
pytest backend/tests                              # full suite
pytest backend/tests/functional -v                # functional only
python backend/scripts/export_swagger.py          # regenerate doc/swagger.yaml
```

Without Nix, `backend/requirements.txt` drives a plain venv. The flake's
`pythonPackages` list and that file must be kept in step.

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r backend/requirements.txt
.venv/bin/python -m pytest backend/tests
```

Frontend, either way:

```sh
npm --prefix frontend install
npm --prefix frontend run dev
```

## Code style

### Python
  - PEP 8, 4-space indent, max line length 100.
  - `snake_case` for modules, functions, variables. `PascalCase` for classes.
    `UPPER_SNAKE_CASE` for constants.
  - Type hints are **mandatory** on every function signature, parameters and
    return type included.
  - Every endpoint declares an explicit `response_model`.
  - No bare `except:`. Catch the specific domain error.
  - No business logic in `main.py`.
  - One aggregate per module: `game.py` exists in `models/`, `repositories/`,
    `services/` and `endpoints/` and the four talk only to their neighbour.
  - Docstrings on public Service methods explaining the rule being enforced.

### Typescript
  - Strict mode on. No `any`.
  - `PascalCase` for components, `camelCase` for functions and variables.
  - Keep API types mirroring the backend response models.

## Testing
  - Functional tests are **mandatory** for every endpoint, covering the happy
    path and every error status the endpoint can return.
  - Unit tests are optional but encouraged for Services holding real rules.
  - A change is not done until the full suite is green. Fix the code, re-run,
    repeat until nothing fails.
  - `nix flake check` runs the same suite against the pinned toolchain. It is
    the one to trust before calling a change finished, since it does not depend
    on whatever happens to be installed locally.
  - Repositories are reset between tests: no shared state leaking across cases.

## Endpoints
  - Creating or modifying an endpoint follows a fixed procedure. See
    `.claude/skills/add-enpoint/SKILL.md` and follow it exactly.

## API documentation
  - `doc/swagger.yaml` is the committed contract of the API and is what the
    frontend is written against. It must never drift from the code.
  - The file is **generated, never hand-edited**. Every endpoint added or
    changed regenerates it in the same change:

    ```sh
    .venv/bin/python backend/scripts/export_swagger.py
    ```

  - `operationId` equals the Python handler name automatically, through
    `generate_unique_id_function` in `app/main.py`. Do not set it by hand.
  - Anything you want in the spec is expressed in the code: `summary`,
    `response_description`, `responses=` (fragments live in
    `app/endpoints/docs.py`), and `Field(description=..., examples=[...])` on
    the models. Tag descriptions and the server list live in `app/config.py`.
  - CI runs the staleness check, which fails on an un-regenerated spec:

    ```sh
    .venv/bin/python backend/scripts/export_swagger.py --check
    ```

  - Live interactive docs are served by the app at `/docs`.

## Commits
  - Conventional Commits only: `type(scope): description`. See
    `.claude/skills/commit-msg/SKILL.md`.

## PR instructions
  - Title format: [<project_name>] <Title>
