import type { Color } from './api'
import { parseFen, type Square } from './fen'

interface BoardProps {
  fen: string
  /** Which side sits at the bottom. */
  orientation: Color
  selected: Square | null
  /** Squares of the move just played, highlighted. */
  lastMove: [string, string] | null
  /** Set while it is not your move, or the game is over. */
  frozen: boolean
  onSquareClick: (square: Square) => void
}

export function Board({
  fen,
  orientation,
  selected,
  lastMove,
  frozen,
  onSquareClick,
}: BoardProps) {
  const squares = parseFen(fen)
  const ordered = orientation === 'white' ? squares : [...squares].reverse()

  return (
    <div className="board" aria-label="chess board">
      {ordered.map((square) => {
        const isSelected = selected?.name === square.name
        const isLastMove = lastMove?.includes(square.name) ?? false
        const classes = [
          'square',
          square.light ? 'light' : 'dark',
          isSelected ? 'selected' : '',
          isLastMove ? 'last-move' : '',
        ]
          .filter(Boolean)
          .join(' ')

        return (
          <button
            key={square.name}
            type="button"
            className={classes}
            disabled={frozen}
            onClick={() => onSquareClick(square)}
            aria-label={square.piece ? `${square.name} ${square.piece}` : square.name}
          >
            {square.glyph ? (
              <span className={`piece ${square.color}`}>{square.glyph}</span>
            ) : null}
          </button>
        )
      })}
    </div>
  )
}
