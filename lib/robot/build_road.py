from lib.gameplay.bank import Bank
from lib.gameplay.board import Board
from lib.gameplay.pieces import PieceType
from lib.gameplay.player import Player
from lib.operations.ops import normalize
from lib.robot.action import Action
from lib.robot.action_type import ActionType
from typing import TYPE_CHECKING
import logging

logger = logging.getLogger(__name__)

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
        self.distance_to_road = self.calculate_distance_to_road()
        self.settlement_unlocks = []
        self.initialize_calculations()

    def calculate_distance_to_road(self) -> int:
        north_path = self.board.shortest_path(
            self.player, self.edge.north_neighbor().id
        )
        south_path = self.board.shortest_path(
            self.player, self.edge.south_neighbor().id
        )
        self.shortest_path = None
        if north_path is None and south_path is None:
            return 1000
        if north_path is not None and south_path is not None:
            self.shortest_path = (
                north_path
                if len(north_path or []) < len(south_path or [])
                else south_path
            )
        elif north_path is not None:
            self.shortest_path = north_path
        elif south_path is not None:
            self.shortest_path = south_path
        else:
            self.shortest_path = None
        return len(self.shortest_path or [])

    def calculate_cost(self) -> float:
        state = self.player_state
        road_cost = 1 - state.purchase_power[PieceType.ROAD]
        cost = road_cost
        if self.distance_to_road > 0:
            # Each road we need to build adds to the cost
            # Cost is exponential to prefer closer settlements
            cost += self.distance_to_road * road_cost
        return normalize(self.parameters["road_building_cost"] * cost)

    def calculate_reward(self) -> float:
        """Road building rewards access to new building locations
        - Longest road
        - Access to new vertices
        - If you're neck and neck with another player for longest road, building a road will give you the edge
        - Cutting off an opponent's road will give you the edge
        """
        # Check to see if this road unlocks important vertices
        reward = 0.0
        settlement_actions = [
            settlement_action.priority
            for settlement_action in self.graph.settlement_actions
            if settlement_action.road_path is not None
            and self.edge in settlement_action.road_path
        ]
        if len(settlement_actions) > 0:
            max_settlement_priority = max(settlement_actions)
            reward += max_settlement_priority

        if len(self.player.resources) > 7:
            reward += self.parameters["road_building_when_abundant_resources"]

        return normalize(self.parameters["road_building_reward"] * reward)

    def can_execute(self, board: "Board", bank: "Bank", player: "Player") -> bool:
        return player.can_build_road_at_edge(self.edge.id, board)

    def execute(
        self, board: Board, bank: Bank, player: Player, players: list[Player]
    ) -> None:
        logger.info(f"{player} building road at {self.edge.id}")
        logger.info(f"{self.player} has abundant resources, building road")
        player.build_road(board, self.edge.id, bank)
        self.executed = True

    def __str__(self) -> str:
        info = {
            "Priority": self.priority,
            "Cost": self.cost,
            "Reward": self.reward,
            "Distance to Road": self.distance_to_road,
            "Shortest Path": self.shortest_path,
        }
        return f"{self.action_type} {self.edge.id} <ul>{''.join([f'<li>{k}: {v}</li>' for k, v in info.items()])}</ul>"
