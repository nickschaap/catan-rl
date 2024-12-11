from lib.gameplay.player import Player
from lib.gameplay.hex import ResourceType, Edge
from lib.robot.action_graph import ActionGraph
from typing import TYPE_CHECKING, Union
import logging

logger = logging.getLogger(__name__)

if TYPE_CHECKING:  # pragma: no cover
    from lib.gameplay.board import Board
    from lib.gameplay.bank import Bank
    from lib.gameplay.game import Game


class Robot(Player):
    def __init__(self, id: int, color: str, game: "Game"):
        super().__init__(id, color)
        self.action_graph = ActionGraph(self, game)

    def take_turn(self, board: "Board", bank: "Bank", players: list["Player"]) -> None:
        # Go through the action graph and execute the actions
        self.action_graph.execute_actions()
