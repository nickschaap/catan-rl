from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from lib.gameplay.bank import Bank
    from lib.gameplay.board import Board
    from lib.gameplay.player import Player
    from lib.robot.action_graph import ActionGraph
    from lib.robot.action_type import ActionType


class Action:
    def __init__(self, action_type: "ActionType", graph: "ActionGraph"):
        self.action_type = action_type
        self.graph = graph
        self.game = graph.game
        self.player = graph.player
        self.board = graph.game.board
        self.player_state = graph.player_state

    def depends_on(self) -> list["Action"]:
        # A dynamic list of actions that should be taken which minimize the cost of the action
        return []

    def cost(self) -> int:
        """The direct cost of the action
        Things that should be considered:
        - The cost of the action
        - The cost of the actions that should be taken before this action
        """
        return 0

    def reward(self) -> int:
        """The reward of the action"""
        return 0

    def priority(self) -> int:
        """The priority of the action"""
        return self.reward() - self.cost()

    def can_execute(self, board: "Board", bank: "Bank", player: "Player") -> bool:
        return True

    def execute(
        self, board: "Board", bank: "Bank", player: "Player", players: list["Player"]
    ) -> None:
        pass

    def __str__(self) -> str:
        return f"{self.action_type}"
