from lib.robot.action import Action
from lib.robot.action_type import ActionType
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from lib.gameplay.bank import Bank
    from lib.gameplay.board import Board
    from lib.gameplay.hex import Edge
    from lib.gameplay.player import Player
    from lib.robot.action_graph import ActionGraph


class BuildRoad(Action):
    def __init__(self, edge: "Edge", graph: "ActionGraph"):
        super().__init__(ActionType.BUILD_ROAD, graph)
        self.edge = edge

    def can_execute(self, board: "Board", bank: "Bank", player: "Player") -> bool:
        return super().can_execute(board, bank, player)

    def __str__(self) -> str:
        return f"{self.action_type} {self.edge.id} <ul><li>Priority: {self.priority()}</li></ul>"
