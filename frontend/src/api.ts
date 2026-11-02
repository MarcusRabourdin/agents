// Typed client for the chess API. The shapes here mirror doc/swagger.yaml -
// if an endpoint changes, this file changes with it.

export type Color = 'white' | 'black'

export type GameStatus =
  | 'waiting'
  | 'in_progress'
  | 'checkmate'
  | 'stalemate'
  | 'draw'
  | 'resigned'

export interface PlayerResponse {
  id: string
  username: string
  rating: number
}

export interface GameStateResponse {
  id: string
  white_player_id: string
  black_player_id: string
  fen: string
  turn: Color
  status: GameStatus
  winner: Color | null
  is_check: boolean
  move_count: number
}

export interface MoveResponse {
  number: number
  color: Color
  uci: string
  san: string
  fen_after: string
}

export interface LegalMovesResponse {
  fen: string
  turn: Color
  /** Every legal move in UCI notation; empty once the game is over. */
  moves: string[]
}

export interface QueueJoinResponse {
  queued: boolean
  game: GameStateResponse | null
}

export const FINISHED_STATUSES: GameStatus[] = [
  'checkmate',
  'stalemate',
  'draw',
  'resigned',
]

export function isOver(status: GameStatus): boolean {
  return FINISHED_STATUSES.includes(status)
}

// Goes through the Vite dev proxy by default, so there is no CORS to deal with
// and a friend on the LAN only needs the dev server's address.
const API_BASE = import.meta.env.VITE_API_BASE ?? '/api'

export class ApiError extends Error {
  readonly status: number

  constructor(status: number, message: string) {
    super(message)
    this.name = 'ApiError'
    this.status = status
  }
}

/** Pulls a readable message out of either error shape FastAPI can return. */
function readDetail(body: unknown, fallback: string): string {
  if (typeof body === 'object' && body !== null && 'detail' in body) {
    const detail = (body as { detail: unknown }).detail
    if (typeof detail === 'string') return detail
    if (Array.isArray(detail)) {
      const first = detail[0] as { msg?: string } | undefined
      if (first?.msg) return first.msg
    }
  }
  return fallback
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let response: Response
  try {
    response = await fetch(`${API_BASE}${path}`, {
      headers: init?.body ? { 'content-type': 'application/json' } : undefined,
      ...init,
    })
  } catch {
    throw new ApiError(0, 'Cannot reach the server. Is the API running?')
  }

  if (response.status === 204) return undefined as T

  const body: unknown = await response.json().catch(() => null)
  if (!response.ok) {
    throw new ApiError(response.status, readDetail(body, response.statusText))
  }
  return body as T
}

function post<T>(path: string, payload: unknown): Promise<T> {
  return request<T>(path, { method: 'POST', body: JSON.stringify(payload) })
}

export const api = {
  createPlayer: (username: string) =>
    post<PlayerResponse>('/players', { username }),

  getPlayer: (playerId: string) =>
    request<PlayerResponse>(`/players/${playerId}`),

  listGames: () => request<GameStateResponse[]>('/games'),

  getGame: (gameId: string) => request<GameStateResponse>(`/games/${gameId}`),

  listMoves: (gameId: string) =>
    request<MoveResponse[]>(`/games/${gameId}/moves`),

  // Fetched once per position rather than per click, so highlighting a piece's
  // moves costs nothing and never waits on the network.
  listLegalMoves: (gameId: string) =>
    request<LegalMovesResponse>(`/games/${gameId}/legal-moves`),

  playMove: (gameId: string, playerId: string, uci: string) =>
    post<GameStateResponse>(`/games/${gameId}/moves`, {
      player_id: playerId,
      uci,
    }),

  resign: (gameId: string, playerId: string) =>
    post<GameStateResponse>(`/games/${gameId}/resign`, { player_id: playerId }),

  joinQueue: (playerId: string) =>
    post<QueueJoinResponse>('/lobby/queue', { player_id: playerId }),

  listQueue: () => request<PlayerResponse[]>('/lobby/queue'),
}
