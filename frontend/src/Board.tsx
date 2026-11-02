import type { Color } from './api'
import { Piece } from './Piece'
import { parseFen, type Square } from './fen'

interface BoardProps {
  fen: string
  /** Which side sits at the bottom. */
  orientation: Color
  selected: Square | null
  /** Squares the selected piece may legally move to. */
  targets: Set<string>
  /** Squares of the move just played, highlighted. */
  lastMove: [string, string] | null
  /** The king standing in check, if any. */
  checkSquare: string | null
  /** Set while it is not your move, or the game is over. */
  frozen: boolean
  onSquareClick: (square: Square) => void
}

export function Board({
  fen,
  orientation,
  selected,
  targets,
  lastMove,
  checkSquare,
  frozen,
  onSquareClick,
}: BoardProps) {
  const squares = parseFen(fen)
  const ordered = orientation === 'white' ? squares : [...squares].reverse()

  return (
    <div className="board" aria-label="chess board">
      {ordered.map((square, index) => {
        const isSelected = selected?.name === square.name
        const isLastMove = lastMove?.includes(square.name) ?? false
        const isTarget = targets.has(square.name)
        // A target that is occupied is a capture: ring it instead of covering
        // the piece with a dot.
        const isCapture = isTarget && square.piece !== null

        const classes = [
          'square',
          square.light ? 'light' : 'dark',
          isSelected ? 'selected' : '',
          isLastMove ? 'last-move' : '',
          checkSquare === square.name ? 'in-check' : '',
        ]
          .filter(Boolean)
          .join(' ')

        // Rank numbers up the left edge, file letters along the bottom edge.
        const rank = index % 8 === 0 ? square.name[1] : null
        const file = index >= 56 ? square.name[0] : null

        return (
          <button
            key={square.name}
            type="button"
            className={classes}
            disabled={frozen}
            onClick={() => onSquareClick(square)}
            aria-label={square.piece ? `${square.name} ${square.piece}` : square.name}
            aria-pressed={isSelected}
          >
            {rank ? <span className="coord coord-rank">{rank}</span> : null}
            {file ? <span className="coord coord-file">{file}</span> : null}
            {square.piece && square.color ? (
              <Piece piece={square.piece} color={square.color} />
            ) : null}
            {isTarget ? (
              <span className={isCapture ? 'move-hint capture' : 'move-hint'} />
            ) : null}
          </button>
        )
      })}
    </div>
  )
}
