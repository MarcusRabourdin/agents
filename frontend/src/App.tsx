import { useCallback, useEffect, useMemo, useState, type FormEvent } from 'react'

import './App.css'
import { Board } from './Board'
import {
  ApiError,
  api,
  isOver,
  type Color,
  type GameStateResponse,
  type MoveResponse,
  type PlayerResponse,
} from './api'
import { findKing, toUci, type Square } from './fen'

const PLAYER_KEY = 'chess.player'
const GAME_KEY = 'chess.gameId'

// There are no websockets yet, so both sides poll. Fast enough to feel like a
// game, slow enough not to hammer the API.
const POLL_MS = 1500

function loadPlayer(): PlayerResponse | null {
  const raw = localStorage.getItem(PLAYER_KEY)
  if (!raw) return null
  try {
    return JSON.parse(raw) as PlayerResponse
  } catch {
    return null
  }
}

function describe(error: unknown): string {
  return error instanceof ApiError ? error.message : 'Something went wrong'
}

function statusLine(game: GameStateResponse, myColor: Color): string {
  const iWon = game.winner === myColor
  switch (game.status) {
    case 'checkmate':
      return iWon ? 'Checkmate - you won' : 'Checkmate - you lost'
    case 'resigned':
      return iWon ? 'Your opponent resigned - you won' : 'You resigned'
    case 'stalemate':
      return 'Stalemate - draw'
    case 'draw':
      return 'Draw'
    default:
      if (game.turn === myColor) return game.is_check ? 'Your move - check' : 'Your move'
      return game.is_check ? 'Opponent to move - check' : 'Waiting for your opponent'
  }
}

export default function App() {
  const [player, setPlayer] = useState<PlayerResponse | null>(loadPlayer)
  const [gameId, setGameId] = useState<string | null>(() =>
    localStorage.getItem(GAME_KEY),
  )
  const [game, setGame] = useState<GameStateResponse | null>(null)
  const [moves, setMoves] = useState<MoveResponse[]>([])
  const [legalMoves, setLegalMoves] = useState<string[]>([])
  const [selected, setSelected] = useState<Square | null>(null)
  const [queued, setQueued] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)
  const [username, setUsername] = useState('')

  useEffect(() => {
    if (player) localStorage.setItem(PLAYER_KEY, JSON.stringify(player))
    else localStorage.removeItem(PLAYER_KEY)
  }, [player])

  useEffect(() => {
    if (gameId) localStorage.setItem(GAME_KEY, gameId)
    else localStorage.removeItem(GAME_KEY)
  }, [gameId])

  const finished = game ? isOver(game.status) : false

  // Follow the game until it ends.
  useEffect(() => {
    if (!gameId || finished) return
    let active = true

    const tick = async () => {
      try {
        const [nextGame, nextMoves, nextLegal] = await Promise.all([
          api.getGame(gameId),
          api.listMoves(gameId),
          api.listLegalMoves(gameId),
        ])
        if (!active) return
        setGame(nextGame)
        setMoves(nextMoves)
        setLegalMoves(nextLegal.moves)
      } catch (caught) {
        if (!active) return
        if (caught instanceof ApiError && caught.status === 404) {
          setGameId(null)
          setGame(null)
        }
        setError(describe(caught))
      }
    }

    void tick()
    const timer = setInterval(() => void tick(), POLL_MS)
    return () => {
      active = false
      clearInterval(timer)
    }
  }, [gameId, finished])

  // While queued, the opponent is the one who gets the game in their response,
  // so this side watches for a game it belongs to.
  useEffect(() => {
    if (!queued || !player || gameId) return
    let active = true

    const tick = async () => {
      try {
        const games = await api.listGames()
        const mine = games.find(
          (candidate) =>
            !isOver(candidate.status) &&
            (candidate.white_player_id === player.id ||
              candidate.black_player_id === player.id),
        )
        if (active && mine) {
          setGameId(mine.id)
          setGame(mine)
          setQueued(false)
        }
      } catch (caught) {
        if (active) setError(describe(caught))
      }
    }

    void tick()
    const timer = setInterval(() => void tick(), POLL_MS)
    return () => {
      active = false
      clearInterval(timer)
    }
  }, [queued, player, gameId])

  const run = useCallback(async (action: () => Promise<void>) => {
    setBusy(true)
    setError(null)
    try {
      await action()
    } catch (caught) {
      setError(describe(caught))
    } finally {
      setBusy(false)
    }
  }, [])

  // Destinations of the selected piece, picked out of the position's legal
  // moves. Promotions appear as several moves to the same square, hence a set.
  const targets = useMemo(() => {
    if (!selected) return new Set<string>()
    return new Set(
      legalMoves
        .filter((uci) => uci.slice(0, 2) === selected.name)
        .map((uci) => uci.slice(2, 4)),
    )
  }, [selected, legalMoves])

  const handleCreatePlayer = (event: FormEvent) => {
    event.preventDefault()
    const name = username.trim()
    if (name.length < 3) {
      setError('Pick a name of at least 3 characters')
      return
    }
    void run(async () => {
      setPlayer(await api.createPlayer(name))
      setUsername('')
    })
  }

  const handleFindOpponent = () => {
    if (!player) return
    void run(async () => {
      const result = await api.joinQueue(player.id)
      if (result.game) {
        setGameId(result.game.id)
        setGame(result.game)
        setQueued(false)
      } else {
        setQueued(true)
      }
    })
  }

  const handleSquareClick = (square: Square) => {
    if (!game || !player) return
    const myColor: Color =
      game.white_player_id === player.id ? 'white' : 'black'

    // Clicking your own piece selects it and reveals where it may go; clicking
    // it again puts it back down.
    if (square.color === myColor) {
      setSelected(selected?.name === square.name ? null : square)
      return
    }
    // Anything that is not a legal destination just clears the selection, so
    // the server is never asked to judge a move the board already showed as
    // impossible.
    if (!selected || !targets.has(square.name)) {
      setSelected(null)
      return
    }

    const uci = toUci(selected, square.name)
    void run(async () => {
      setGame(await api.playMove(game.id, player.id, uci))
      const [nextMoves, nextLegal] = await Promise.all([
        api.listMoves(game.id),
        api.listLegalMoves(game.id),
      ])
      setMoves(nextMoves)
      setLegalMoves(nextLegal.moves)
    }).finally(() => setSelected(null))
  }

  const handleResign = () => {
    if (!game || !player) return
    if (!confirm('Resign this game?')) return
    void run(async () => {
      setGame(await api.resign(game.id, player.id))
    })
  }

  const handleLeaveGame = () => {
    setGameId(null)
    setGame(null)
    setMoves([])
    setLegalMoves([])
    setSelected(null)
    setError(null)
  }

  const handleSignOut = () => {
    handleLeaveGame()
    setPlayer(null)
    setQueued(false)
  }

  if (!player) {
    return (
      <main className="shell">
        <h1>Chess</h1>
        <p className="muted">Pick a name to get a player id.</p>
        <form className="row" onSubmit={handleCreatePlayer}>
          <input
            value={username}
            onChange={(event) => setUsername(event.target.value)}
            placeholder="your name"
            minLength={3}
            maxLength={32}
            autoFocus
          />
          <button type="submit" disabled={busy}>
            {busy ? 'Creating...' : 'Start'}
          </button>
        </form>
        {error ? <p className="error">{error}</p> : null}
      </main>
    )
  }

  if (!gameId || !game) {
    return (
      <main className="shell">
        <h1>Chess</h1>
        <p className="muted">
          {player.username} &middot; rating {player.rating}
        </p>
        {queued ? (
          <>
            <p className="waiting">Waiting for an opponent to join...</p>
            <p className="muted">
              Your friend opens this same page, picks a name, and hits
              &ldquo;Find an opponent&rdquo;.
            </p>
          </>
        ) : (
          <button type="button" onClick={handleFindOpponent} disabled={busy}>
            {busy ? 'Joining...' : 'Find an opponent'}
          </button>
        )}
        {error ? <p className="error">{error}</p> : null}
        <button type="button" className="link" onClick={handleSignOut}>
          switch player
        </button>
      </main>
    )
  }

  const myColor: Color = game.white_player_id === player.id ? 'white' : 'black'
  const myTurn = game.turn === myColor && !finished
  const lastUci = moves.at(-1)?.uci
  const lastMove: [string, string] | null = lastUci
    ? [lastUci.slice(0, 2), lastUci.slice(2, 4)]
    : null

  return (
    <main className="shell wide">
      <header className="bar">
        <strong>{player.username}</strong>
        <span className="muted">plays {myColor}</span>
      </header>

      <p className={myTurn ? 'turn active' : 'turn'}>
        {statusLine(game, myColor)}
      </p>

      <Board
        fen={game.fen}
        orientation={myColor}
        selected={selected}
        targets={targets}
        lastMove={lastMove}
        checkSquare={game.is_check ? findKing(game.fen, game.turn) : null}
        frozen={busy || !myTurn}
        onSquareClick={handleSquareClick}
      />

      {error ? <p className="error">{error}</p> : null}

      <ol className="moves">
        {moves.map((move) => (
          <li key={move.number}>{move.san}</li>
        ))}
      </ol>

      <footer className="row">
        {finished ? (
          <button type="button" onClick={handleLeaveGame}>
            Back to the lobby
          </button>
        ) : (
          <button type="button" onClick={handleResign} disabled={busy}>
            Resign
          </button>
        )}
      </footer>
    </main>
  )
}
