from enum import Enum


class GameState(Enum):
    NOT_READY = 1
    IN_PROGRESS = 2
    FINISHED = 3