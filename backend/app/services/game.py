"""Game business logic.

Every chess rule - legality, check, checkmate, stalemate, draw - is delegated to
`python-chess`. Nothing here re-implements the rules of the game.

Checks are always applied in this order, so the status code a caller gets is
predictable: the game must exist (404), the caller must be one of its two
players (403), the game must still be running and it must be their turn (409),
and only then is the move itself judged (422).
"""

from uuid import uuid4

import chess

from app.errors import (
    CannotPlayAgainstSelfError,
    GameAlreadyOverError,
    GameNotFoundError,
    IllegalMoveError,
    NotAPlayerOfGameError,
    NotPlayerTurnError,
)
from app.models.game import (
    Color,
    Game,
    GameStateResponse,
    GameStatus,
    LegalMovesResponse,
    Move,
    MoveResponse,
)
from app.repositories.game import GameRepository
from app.services.player import PlayerService

_TERMINATION_STATUS = {
    chess.Termination.CHECKMATE: GameStatus.CHECKMATE,
    chess.Termination.STALEMATE: GameStatus.STALEMATE,
}


class GameService:
    def __init__(self, games: GameRepository, players: PlayerService) -> None:
        self._games = games
        self._players = players

    def create_game(self, white_player_id: str, black_player_id: str) -> GameStateResponse:
        """Open a game between two existing, distinct players. White moves first."""
        self._players.require_player(white_player_id)
        self._players.require_player(black_player_id)
        if white_player_id == black_player_id:
            raise CannotPlayAgainstSelfError(white_player_id)

        game = Game(
            id=str(uuid4()),
            white_player_id=white_player_id,
            black_player_id=black_player_id,
        )
        return self._to_state(self._games.add(game))

    def get_game(self, game_id: str) -> GameStateResponse:
        return self._to_state(self._require_game(game_id))

    def list_games(self, status: GameStatus | None = None) -> list[GameStateResponse]:
        games = self._games.list() if status is None else self._games.list_by_status(status)
        return [self._to_state(game) for game in games]

    def list_moves(self, game_id: str) -> list[MoveResponse]:
        game = self._require_game(game_id)
        return [MoveResponse.from_move(move) for move in game.moves]

    def list_legal_moves(self, game_id: str) -> LegalMovesResponse:
        """Every move the side to move may play right now.

        A finished game has no playable move, whatever its last position says,
        so the list comes back empty rather than tempting a caller to offer a
        move the API would refuse.
        """
        game = self._require_game(game_id)
        board = chess.Board(game.fen)
        moves = [] if game.status.is_over else [move.uci() for move in board.legal_moves]
        return LegalMovesResponse(
            fen=game.fen,
            turn=self._turn_of(board),
            moves=moves,
        )

    def play_move(self, game_id: str, player_id: str, uci: str) -> GameStateResponse:
        """Play one move for `player_id`.

        Rejects a move by someone who is not in the game, a move in a finished
        game, a move played out of turn, and a move that is illegal in the
        current position.
        """
        game = self._require_game(game_id)
        color = self._color_of(game, player_id)
        self._require_running(game)

        board = chess.Board(game.fen)
        if color != self._turn_of(board):
            raise NotPlayerTurnError(player_id)

        move = self._parse_move(board, uci)
        san = board.san(move)
        board.push(move)

        game.moves.append(
            Move(
                number=len(game.moves) + 1,
                color=color,
                uci=move.uci(),
                san=san,
                fen_after=board.fen(),
            )
        )
        game.fen = board.fen()
        game.status, game.winner = self._outcome_of(board)
        return self._to_state(self._games.update(game))

    def resign(self, game_id: str, player_id: str) -> GameStateResponse:
        """Resign a running game. The opponent wins."""
        game = self._require_game(game_id)
        color = self._color_of(game, player_id)
        self._require_running(game)

        game.status = GameStatus.RESIGNED
        game.winner = Color.BLACK if color is Color.WHITE else Color.WHITE
        return self._to_state(self._games.update(game))

    def _require_game(self, game_id: str) -> Game:
        game = self._games.get(game_id)
        if game is None:
            raise GameNotFoundError(game_id)
        return game

    @staticmethod
    def _require_running(game: Game) -> None:
        if game.status.is_over:
            raise GameAlreadyOverError(game.id, game.status.value)

    @staticmethod
    def _color_of(game: Game, player_id: str) -> Color:
        if player_id == game.white_player_id:
            return Color.WHITE
        if player_id == game.black_player_id:
            return Color.BLACK
        raise NotAPlayerOfGameError(player_id, game.id)

    @staticmethod
    def _turn_of(board: chess.Board) -> Color:
        return Color.WHITE if board.turn == chess.WHITE else Color.BLACK

    @staticmethod
    def _parse_move(board: chess.Board, uci: str) -> chess.Move:
        try:
            move = chess.Move.from_uci(uci)
        except ValueError as exc:
            raise IllegalMoveError(uci) from exc
        if move not in board.legal_moves:
            raise IllegalMoveError(uci)
        return move

    @staticmethod
    def _outcome_of(board: chess.Board) -> tuple[GameStatus, Color | None]:
        outcome = board.outcome(claim_draw=True)
        if outcome is None:
            return GameStatus.IN_PROGRESS, None

        status = _TERMINATION_STATUS.get(outcome.termination, GameStatus.DRAW)
        if outcome.winner is None:
            return status, None
        winner = Color.WHITE if outcome.winner else Color.BLACK
        return status, winner

    def _to_state(self, game: Game) -> GameStateResponse:
        board = chess.Board(game.fen)
        return GameStateResponse(
            id=game.id,
            white_player_id=game.white_player_id,
            black_player_id=game.black_player_id,
            fen=game.fen,
            turn=self._turn_of(board),
            status=game.status,
            winner=game.winner,
            is_check=board.is_check(),
            move_count=len(game.moves),
        )
