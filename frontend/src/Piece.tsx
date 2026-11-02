import type { Color } from './api'
import { PIECE_DETAILS, PIECE_SHAPES, type Primitive } from './pieceShapes'

const NAMES: Record<string, string> = {
  p: 'pawn',
  r: 'rook',
  n: 'knight',
  b: 'bishop',
  q: 'queen',
  k: 'king',
}

function draw(primitive: Primitive, index: number) {
  return 'd' in primitive ? (
    <path key={index} d={primitive.d} />
  ) : (
    <circle key={index} cx={primitive.cx} cy={primitive.cy} r={primitive.r} />
  )
}

interface PieceProps {
  /** FEN letter; case picks the colour, the shape is shared. */
  piece: string
  color: Color
}

export function Piece({ piece, color }: PieceProps) {
  const type = piece.toLowerCase()
  const shapes = PIECE_SHAPES[type]
  if (!shapes) return null

  const detail = PIECE_DETAILS[type]
  const body = shapes.map(draw)

  return (
    <svg
      className={`piece ${color}`}
      viewBox="0 0 45 45"
      role="img"
      aria-label={`${color} ${NAMES[type] ?? type}`}
    >
      {/* Outline pass: a fat stroke under the body, so only its outer half shows. */}
      <g className="piece-outline">{body}</g>
      <g className="piece-body">{body}</g>
      {detail ? <path className="piece-detail" d={detail} /> : null}
    </svg>
  )
}
