from enum import Enum


class ActionType(Enum):
    BUILD_ROAD = 1
    BUILD_SETTLEMENT = 2
    BUILD_CITY = 3
    BUY_DEVELOPMENT_CARD = 4
    PLAY_DEVELOPMENT_CARD = 5

    def __str__(self):
        return self.name
