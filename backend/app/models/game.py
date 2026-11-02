"""Game models: the domain objects and their request/response schemas."""

from enum import Enum

from pydantic import BaseModel, Field

from app.models.common import Entity

STARTING_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"

UCI_PATTERN = r"^[a-h][1-8][a-h][1-8][qrbn]?$"


class Color(str, Enum):
    WHITE = "white"
    BLACK = "black"


class GameStatus(str, Enum):
    WAITING = "waiting"
    IN_PROGRESS = "in_progress"
    CHECKMATE = "checkmate"
    STALEMATE = "stalemate"
    DRAW = "draw"
    RESIGNED = "resigned"

    @property
    def is_over(self) -> bool:
        return self in _FINISHED_STATUSES


_FINISHED_STATUSES = frozenset(
    {GameStatus.CHECKMATE, GameStatus.STALEMATE, GameStatus.DRAW, GameStatus.RESIGNED}
)


class Move(BaseModel):
    """One move played in a game, as stored by the Repository layer."""

    number: int
    color: Color
    uci: str
    san: str
    fen_after: str


class Game(Entity):
    """A game, as stored by the Repository layer."""

    white_player_id: str
    black_player_id: str
    fen: str = STARTING_FEN
    status: GameStatus = GameStatus.IN_PROGRESS
    winner: Color | None = None
    moves: list[Move] = Field(default_factory=list)


class GameCreateRequest(BaseModel):
    white_player_id: str
    black_player_id: str


class MoveRequest(BaseModel):
    player_id: str
    uci: str = Field(
        pattern=UCI_PATTERN,
        description="Move in UCI notation, promotion suffixed (e.g. e7e8q)",
        examples=["e2e4"],
    )


class ResignRequest(BaseModel):
    player_id: str


class MoveResponse(BaseModel):
    number: int = Field(description="1-based index of the move in the game", examples=[1])
    color: Color
    uci: str = Field(examples=["e2e4"])
    san: str = Field(description="Standard Algebraic Notation", examples=["e4"])
    fen_after: str

    @classmethod
    def from_move(cls, move: Move) -> "MoveResponse":
        return cls(
            number=move.number,
            color=move.color,
            uci=move.uci,
            san=move.san,
            fen_after=move.fen_after,
        )


class LegalMovesResponse(BaseModel):
    """Every move playable in the current position.

    The position is echoed back so a caller that polls can tell whether the
    list it holds still describes the board it is drawing.
    """

    fen: str = Field(
        description="Position the moves were generated from",
        examples=[STARTING_FEN],
    )
    turn: Color = Field(description="Side the moves belong to")
    moves: list[str] = Field(
        description="Legal moves in UCI notation, empty once the game is over",
        examples=[["e2e4", "g1f3"]],
    )


class GameStateResponse(BaseModel):
    id: str
    white_player_id: str
    black_player_id: str
    fen: str = Field(
        description="Current position in Forsyth-Edwards Notation",
        examples=[STARTING_FEN],
    )
    turn: Color
    status: GameStatus
    winner: Color | None = Field(
        default=None, description="Null while the game is not decided"
    )
    is_check: bool
    move_count: int = Field(examples=[0])
