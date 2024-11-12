from lib.gameplay.player import Player
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from lib.gameplay.board import Board
    from lib.gameplay.bank import Bank


class Robot(Player):
    def __init__(self, id: int, color: str):
        super().__init__(id, color)

    def take_turn(self, board: "Board", bank: "Bank", players: list["Player"]) -> None:
        pass
