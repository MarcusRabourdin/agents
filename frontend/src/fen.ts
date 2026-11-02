// FEN helpers. The board is a flat array of 64 entries, index 0 = a8, 63 = h1,
// which is the order a board renders in.

import type { Color } from './api'

export const FILES = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'] as const

/** Square names in render order: a8, b8, ... h1. */
export const SQUARES: string[] = Array.from({ length: 64 }, (_, index) => {
  const file = FILES[index % 8]
  const rank = 8 - Math.floor(index / 8)
  return `${file}${rank}`
})

export interface Square {
  /** Algebraic name, e.g. "e4". */
  name: string
  /** FEN letter of the piece standing there, or null. */
  piece: string | null
  /** Colour of the piece, or null when the square is empty. */
  color: Color | null
  /** True for the light-coloured half of the board. */
  light: boolean
}

/** Expands the placement field of a FEN into 64 squares in render order. */
export function parseFen(fen: string): Square[] {
  const placement = fen.split(' ')[0] ?? ''
  const pieces: (string | null)[] = []

  for (const rank of placement.split('/')) {
    for (const symbol of rank) {
      const empty = Number.parseInt(symbol, 10)
      if (Number.isNaN(empty)) {
        pieces.push(symbol)
      } else {
        pieces.push(...Array.from({ length: empty }, () => null))
      }
    }
  }

  return SQUARES.map((name, index) => {
    const piece = pieces[index] ?? null
    const file = index % 8
    const rank = Math.floor(index / 8)
    return {
      name,
      piece,
      color: piece ? (piece === piece.toUpperCase() ? 'white' : 'black') : null,
      light: (file + rank) % 2 === 0,
    }
  })
}

/** Where the given side's king stands, for highlighting a check. */
export function findKing(fen: string, color: Color): string | null {
  const king = color === 'white' ? 'K' : 'k'
  return parseFen(fen).find((square) => square.piece === king)?.name ?? null
}

/**
 * Builds the UCI string for a move, auto-promoting to a queen.
 *
 * Promotion choice is deliberately not offered: a queen is what you want
 * almost every time, and the server validates the rest.
 */
export function toUci(from: Square, to: string): string {
  const targetRank = to[1]
  const promoting =
    from.piece?.toLowerCase() === 'p' &&
    ((from.color === 'white' && targetRank === '8') ||
      (from.color === 'black' && targetRank === '1'))
  return `${from.name}${to}${promoting ? 'q' : ''}`
}
