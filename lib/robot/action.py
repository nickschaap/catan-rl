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
        self.parameters = graph.game.parameters(self.player)
        self.executed = False

    def initialize_calculations(self) -> None:
        self.cost = self.calculate_cost()
        self.reward = self.calculate_reward()
        self.priority = self.calculate_priority()

    def calculate_cost(self) -> float:
        """The direct cost of the action
        Things that should be considered:
        - The cost of the action
        - The cost of the actions that should be taken before this action
        """
        return 0

    def calculate_reward(self) -> float:
        """The reward of the action"""
        return 0

    def calculate_priority(self) -> float:
        """The priority of the action"""
        return self.reward - self.cost

    def can_execute(self, board: "Board", bank: "Bank", player: "Player") -> bool:
        return True

    def execute(
        self, board: "Board", bank: "Bank", player: "Player", players: list["Player"]
    ) -> None:
        self.executed = True

    def __str__(self) -> str:
        info = {
            "Priority": self.priority,
            "Cost": self.cost,
            "Reward": self.reward,
        }
        return f"{self.action_type} <ul>{''.join([f'<li>{k}: {v}</li>' for k, v in info.items()])}</ul>"
