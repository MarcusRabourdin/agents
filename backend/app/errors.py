"""Domain errors.

The Service layer raises these. The Endpoint layer is the only layer allowed to
translate them into an `HTTPException`, see `.claude/skills/add-enpoint`.
"""


class ChessPlatformError(Exception):
    """Base class for every domain error of the platform."""


class NotFoundError(ChessPlatformError):
    """Something was asked for by id and does not exist. Maps to 404."""


class PlayerNotFoundError(NotFoundError):
    def __init__(self, player_id: str) -> None:
        super().__init__(f"player {player_id} not found")


class GameNotFoundError(NotFoundError):
    def __init__(self, game_id: str) -> None:
        super().__init__(f"game {game_id} not found")


class ForbiddenError(ChessPlatformError):
    """The caller exists but is not allowed to act here. Maps to 403."""


class NotAPlayerOfGameError(ForbiddenError):
    def __init__(self, player_id: str, game_id: str) -> None:
        super().__init__(f"player {player_id} is not a player of game {game_id}")


class ConflictError(ChessPlatformError):
    """The current state does not allow the action. Maps to 409."""


class UsernameAlreadyTakenError(ConflictError):
    def __init__(self, username: str) -> None:
        super().__init__(f"username {username!r} is already taken")


class NotPlayerTurnError(ConflictError):
    def __init__(self, player_id: str) -> None:
        super().__init__(f"it is not player {player_id}'s turn")


class GameAlreadyOverError(ConflictError):
    def __init__(self, game_id: str, status: str) -> None:
        super().__init__(f"game {game_id} is already over ({status})")


class AlreadyQueuedError(ConflictError):
    def __init__(self, player_id: str) -> None:
        super().__init__(f"player {player_id} is already in the queue")


class InvalidInputError(ChessPlatformError):
    """The input is well formed but a business rule rejects it. Maps to 422."""


class IllegalMoveError(InvalidInputError):
    def __init__(self, uci: str) -> None:
        super().__init__(f"{uci} is not a legal move in the current position")


class CannotPlayAgainstSelfError(InvalidInputError):
    def __init__(self, player_id: str) -> None:
        super().__init__(f"player {player_id} cannot play against themselves")
