// Geometry for the chess pieces, on a 45x45 board square.
//
// The Unicode glyphs could not be used: the white set (♔♕♖) is hollow by
// design, so a white king read as an outline instead of a piece. Every shape
// below is a solid silhouette.
//
// A piece is a list of overlapping primitives whose union is the piece. They
// are painted twice: once as a fat stroke that becomes the outline, then once
// filled on top. The fill pass hides the seams where primitives meet, so the
// result is one solid body with a single clean edge - no holes, no inner lines.

/** One drawing primitive: a path, or a circle. */
export type Primitive = { d: string } | { cx: number; cy: number; r: number }

/** The plinth every piece stands on. */
const BASE: Primitive = {
  d: 'M 10.7 36 h 23.6 a 2.2 2.2 0 0 1 2.2 2.2 v 0.6 a 2.2 2.2 0 0 1 -2.2 2.2 h -23.6 a 2.2 2.2 0 0 1 -2.2 -2.2 v -0.6 a 2.2 2.2 0 0 1 2.2 -2.2 z',
}

/** FEN letter (lowercase) to the primitives that make up the piece. */
export const PIECE_SHAPES: Record<string, Primitive[]> = {
  p: [
    { cx: 22.5, cy: 13.5, r: 5.4 },
    { d: 'M 17.6 18 h 9.8 l -0.9 3.4 h -8 z' },
    { d: 'M 18.6 21 h 7.8 c 0 7 4 11 6.1 15.4 h -20 c 2.1 -4.4 6.1 -8.4 6.1 -15.4 z' },
    BASE,
  ],
  r: [
    { d: 'M 11 7.5 h 5 v 4 h 3.6 v -4 h 5.8 v 4 h 3.6 v -4 h 5 v 10 h -23 z' },
    { d: 'M 13.4 17.5 h 18.2 l -1.6 4.7 h -15 z' },
    { d: 'M 15 22 h 15 c 0 6.4 1.1 10.4 2.6 14 h -20.2 c 1.5 -3.6 2.6 -7.6 2.6 -14 z' },
    BASE,
  ],
  n: [
    {
      // Horse head in profile, facing left: chest, jaw, muzzle, brow, ear, nape.
      d: 'M 14.5 36 C 13.8 30.5 14.6 26.2 17.2 23.4 C 15.4 24.4 13.2 25.2 11.6 24.6 C 9.8 24 9.4 21.8 10.8 20.4 C 12.6 18.6 15.4 17.2 17.6 15.2 C 19.8 13.2 21.4 10.6 22.2 7.6 C 23.2 8.6 24.6 9.4 26.2 9.6 C 26.4 7.4 27.2 5.2 28.8 3.4 C 31.4 5.6 32.8 8.6 33.6 12 C 35 18 35.4 27 34.6 36 Z',
    },
    BASE,
  ],
  b: [
    { cx: 22.5, cy: 7, r: 2.6 },
    {
      d: 'M 22.5 8.4 c 5.2 2.2 8.2 7.4 8.2 11.4 c 0 3 -1.8 5.2 -3.8 6.2 h -8.8 c -2 -1 -3.8 -3.2 -3.8 -6.2 c 0 -4 3 -9.2 8.2 -11.4 z',
    },
    { d: 'M 15.4 25.6 h 14.2 c 1.2 2.2 0.2 4.4 -2 4.4 h -10.2 c -2.2 0 -3.2 -2.2 -2 -4.4 z' },
    { d: 'M 18 30 h 9 c 0 4.2 2.3 6.4 5.6 6 h -20.2 c 3.3 0.4 5.6 -1.8 5.6 -6 z' },
    BASE,
  ],
  q: [
    { cx: 9.8, cy: 10.4, r: 2.5 },
    { cx: 16, cy: 7.2, r: 2.5 },
    { cx: 22.5, cy: 6, r: 2.5 },
    { cx: 29, cy: 7.2, r: 2.5 },
    { cx: 35.2, cy: 10.4, r: 2.5 },
    { d: 'M 9.8 10.6 L 14.6 22 h 15.8 L 35.2 10.6 L 29 17.4 L 22.5 6.4 L 16 17.4 Z' },
    { d: 'M 13.6 21.6 h 17.8 c 1.2 2.4 0.2 4.6 -2.2 4.6 h -13.4 c -2.4 0 -3.4 -2.2 -2.2 -4.6 z' },
    { d: 'M 16 26 h 13 c 0 5.4 2 8.4 4.2 10 h -21.4 c 2.2 -1.6 4.2 -4.6 4.2 -10 z' },
    BASE,
  ],
  k: [
    { d: 'M 21 3 h 3 v 4.4 h 4.4 v 3 h -4.4 v 5 h -3 v -5 h -4.4 v -3 h 4.4 z' },
    {
      d: 'M 22.5 13.4 c 6.1 0 11 4 11 9 c 0 2.2 -1 4 -2.1 5.2 h -17.8 c -1.1 -1.2 -2.1 -3 -2.1 -5.2 c 0 -5 4.9 -9 11 -9 z',
    },
    { d: 'M 13.2 27 h 18.6 c 1.2 2.2 0.2 4.4 -2 4.4 h -14.6 c -2.2 0 -3.2 -2.2 -2 -4.4 z' },
    { d: 'M 16 31.2 h 13 c 0 3 2 4.2 4.2 4.8 h -21.4 c 2.2 -0.6 4.2 -1.8 4.2 -4.8 z' },
    BASE,
  ],
}

/** Lines drawn over the finished body, where a flat silhouette loses detail. */
export const PIECE_DETAILS: Record<string, string | null> = {
  p: null,
  r: 'M 13.4 17.6 h 18.2',
  n: 'M 19.2 15.8 l 2.1 -1.5 M 26.6 10.2 C 28.4 14 29.4 19.6 29.4 25.4',
  b: 'M 19.4 13.6 l 6.2 7.4',
  q: 'M 13.9 22 h 17.2',
  k: 'M 13.4 27.2 h 18.2',
}
