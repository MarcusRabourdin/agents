# Frontend

Minimal React + TypeScript + Vite client for the chess API. Enough to play a
real game against a friend, nothing more.

## Run it

Two processes. Backend first:

```sh
# terminal 1, from the repository root
nix run .#                      # or: uvicorn app.main:app --reload --app-dir backend
```

```sh
# terminal 2, from the repository root
npm --prefix frontend install   # first time only
npm --prefix frontend run dev
```

Open http://localhost:5173.

## Playing against a friend

The dev server proxies `/api` to the backend, so the browser only ever talks to
one origin and there is no CORS to configure.

On the same machine, two browser windows are enough - the player id lives in
`localStorage`, so use two different profiles or one normal and one private
window, otherwise both tabs share the same player.

For a friend on your network, expose the dev server:

```sh
npm --prefix frontend run dev -- --host
```

Vite prints a `Network:` address. Your friend opens that. Only the dev server
needs to be reachable; it forwards the API calls for them.

Then, both of you:

1. Pick a name, press **Start**.
2. Press **Find an opponent**. The first one waits, the second is matched and
   the game opens on both screens.
3. Click one of your pieces, then its destination. The server validates the
   move; an illegal one comes back as a message under the board.

## How it works

| File | Role |
|------|------|
| `src/api.ts` | Typed client. Shapes mirror `doc/swagger.yaml`. |
| `src/fen.ts` | FEN to 64 squares, and UCI building. |
| `src/Board.tsx` | The board. Click a piece, click a target. |
| `src/App.tsx` | Three screens: name, lobby, game. Polling lives here. |

Deliberate choices:

- **No chess library on the client.** The server owns every rule, so the client
  sends `from+to` and renders whatever position comes back. One source of truth.
- **Polling, not websockets.** Both sides poll every 1.5s, so the opponent's
  move takes up to that long to appear. The API has no socket yet.
- **Auto-queens.** A pawn reaching the last rank promotes to a queen with no
  dialog.
- **No auth.** The player id is held in `localStorage` and sent in the body;
  anyone who knows an id can move for that player.

## Scripts

```sh
npm --prefix frontend run dev        # dev server
npm --prefix frontend run build      # typecheck + production build
npm --prefix frontend run typecheck  # tsc only
npm --prefix frontend run lint       # oxlint
```

Point the client at a different backend with `CHESS_API_TARGET` (dev proxy) or
`VITE_API_BASE` (bypasses the proxy, needs CORS on the API).
