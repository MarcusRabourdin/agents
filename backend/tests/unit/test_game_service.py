"""Unit tests for the rules enforced by GameService."""

import pytest

from app.errors import (
    CannotPlayAgainstSelfError,
    GameNotFoundError,
    IllegalMoveError,
    NotAPlayerOfGameError,
    NotPlayerTurnError,
    PlayerNotFoundError,
)
from app.models.game import Color, GameStatus
from app.repositories.game import GameRepository
from app.repositories.player import PlayerRepository
from app.services.game import GameService
from app.services.player import PlayerService

# Black mates in two: 1. f3 e5 2. g4 Qh4#
FOOLS_MATE = ["f2f3", "e7e5", "g2g4", "d8h4"]

# White to move, Qa7-f7 leaves black with no legal move and no check.
ONE_MOVE_FROM_STALEMATE = "7k/Q7/6K1/8/8/8/8/8 w - - 0 1"


class Fixture:
    def __init__(self) -> None:
        self.games_repo = GameRepository()
        self.players = PlayerService(PlayerRepository())
        self.service = GameService(self.games_repo, self.players)
        self.white = self.players.create_player("white_side").id
        self.black = self.players.create_player("black_side").id

    def new_game(self) -> str:
        return self.service.create_game(self.white, self.black).id

    def force_position(self, game_id: str, fen: str) -> None:
        """Drop a position straight into storage to test an endgame."""
        game = self.games_repo.get(game_id)
        assert game is not None
        game.fen = fen
        self.games_repo.update(game)


@pytest.fixture
def fix() -> Fixture:
    return Fixture()


def test_create_game_requires_both_players_to_exist(fix: Fixture) -> None:
    with pytest.raises(PlayerNotFoundError):
        fix.service.create_game(fix.white, "ghost")


def test_create_game_refuses_a_single_player(fix: Fixture) -> None:
    with pytest.raises(CannotPlayAgainstSelfError):
        fix.service.create_game(fix.white, fix.white)


def test_get_game_unknown_raises(fix: Fixture) -> None:
    with pytest.raises(GameNotFoundError):
        fix.service.get_game("ghost")


def test_play_move_refuses_an_outsider(fix: Fixture) -> None:
    game_id = fix.new_game()

    with pytest.raises(NotAPlayerOfGameError):
        fix.service.play_move(game_id, "ghost", "e2e4")


def test_play_move_refuses_a_move_out_of_turn(fix: Fixture) -> None:
    game_id = fix.new_game()

    with pytest.raises(NotPlayerTurnError):
        fix.service.play_move(game_id, fix.black, "e7e5")


def test_play_move_refuses_an_illegal_move(fix: Fixture) -> None:
    game_id = fix.new_game()

    with pytest.raises(IllegalMoveError):
        fix.service.play_move(game_id, fix.white, "e2e5")


def test_play_move_alternates_the_turn(fix: Fixture) -> None:
    game_id = fix.new_game()

    assert fix.service.play_move(game_id, fix.white, "e2e4").turn is Color.BLACK
    assert fix.service.play_move(game_id, fix.black, "e7e5").turn is Color.WHITE


def test_play_move_records_san_notation(fix: Fixture) -> None:
    game_id = fix.new_game()
    fix.service.play_move(game_id, fix.white, "g1f3")

    moves = fix.service.list_moves(game_id)

    assert [move.san for move in moves] == ["Nf3"]


def test_play_move_detects_checkmate(fix: Fixture) -> None:
    game_id = fix.new_game()
    for uci, player in zip(FOOLS_MATE, [fix.white, fix.black] * 2, strict=True):
        state = fix.service.play_move(game_id, player, uci)

    assert state.status is GameStatus.CHECKMATE
    assert state.winner is Color.BLACK


def test_play_move_detects_stalemate_without_a_winner(fix: Fixture) -> None:
    game_id = fix.new_game()
    fix.force_position(game_id, ONE_MOVE_FROM_STALEMATE)

    state = fix.service.play_move(game_id, fix.white, "a7f7")

    assert state.status is GameStatus.STALEMATE
    assert state.winner is None
    assert state.is_check is False


def test_resign_hands_the_win_to_the_opponent(fix: Fixture) -> None:
    game_id = fix.new_game()

    state = fix.service.resign(game_id, fix.black)

    assert state.status is GameStatus.RESIGNED
    assert state.winner is Color.WHITE


def test_list_games_filters_on_status(fix: Fixture) -> None:
    running = fix.new_game()
    finished = fix.new_game()
    fix.service.resign(finished, fix.white)

    in_progress = fix.service.list_games(GameStatus.IN_PROGRESS)

    assert [state.id for state in in_progress] == [running]
    assert len(fix.service.list_games()) == 2
