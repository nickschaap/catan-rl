from lib.gameplay.hex import ResourceType
from lib.gameplay.pieces import PieceType
from lib.operations.ops import normalize
from lib.robot.action_type import ActionType
from lib.robot.action import Action
from typing import TYPE_CHECKING, Union

import logging

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from lib.gameplay.hex import Vertex
    from lib.robot.action_graph import ActionGraph
    from lib.gameplay.hex import Edge
    from lib.gameplay.bank import Bank
    from lib.gameplay.board import Board
    from lib.gameplay.player import Player


class BuildSettlement(Action):
    def __init__(self, vertex: "Vertex", graph: "ActionGraph"):
        super().__init__(ActionType.BUILD_SETTLEMENT, graph)
        self.vertex = vertex
        self.road_path = self.min_distance_to_road()
        self.resource_unlocks = self.resources_at_vertex()
        self.initialize_calculations()

    def calculate_cost(self) -> float:
        """The direct cost of the action
        Things that should be considered:
        - The minimum distance to a road owned by the player (dynamic)
        - The resources required to build the settlement (constant)
        """
        state = self.graph.player_state
        # Base cost for building a settlement
        cost = 1 - state.purchase_power[PieceType.SETTLEMENT]
        road_cost = 1 - state.purchase_power[PieceType.ROAD]

        if self.road_path is None:
            cost = 10  # Impossible to build here
            return cost * self.parameters["settlement_building_cost"]
        else:
            # Add distance penalty based on how far we need to build roads to reach this vertex
            if len(self.road_path) > 0:
                # Each road we need to build adds to the cost
                # Cost is exponential to prefer closer settlements
                cost += len(self.road_path) * road_cost

        return normalize(self.parameters["settlement_building_cost"] * cost)

    def calculate_reward(self) -> float:
        """Reward
        - The resources at the vertex
        - Get access to more likely resources
        - To get another victory point
        """
        state = self.graph.player_state
        resource_importance = state.resource_importance
        # Sum of unlocked resources weighted by likelihood and importance
        reward = sum(resource_importance[r[0]] * r[1] for r in self.resource_unlocks)

        return normalize(self.parameters["settlement_building_reward"] * reward)

    def min_distance_to_road(self) -> Union[list["Edge"], None]:
        return self.board.shortest_path(self.player, self.vertex.id)

    def resources_at_vertex(self) -> list[tuple[ResourceType, float]]:
        return [
            (hex.resourceType, hex.likelihood())
            for hex in self.vertex.get_hexes()
            if hex.resourceType is not None
        ]

    def can_execute(self, board: "Board", bank: "Bank", player: "Player") -> bool:
        return player.can_build_settlement_at_vertex(self.vertex.id, board)

    def execute(
        self, board: "Board", bank: "Bank", player: "Player", players: list["Player"]
    ) -> None:
        logger.info(f"{player} building settlement at {self.vertex.id}")
        player.build_settlement(board, self.vertex.id, bank)
        self.executed = True

    def __str__(self) -> str:
        info = {
            "Min Distance to Road": [str(edge) for edge in self.road_path or []]
            if self.road_path is not None
            else "None",
            "Resources at Vertex": ", ".join(
                [f"{resource}" for resource in self.resource_unlocks]
            ),
            "Priority": self.priority,
            "Cost": self.cost,
            "Reward": self.reward,
        }
        return f"{self.action_type} ({self.vertex.id}) <ul>{''.join([f'<li>{k}: {v}</li>' for k, v in info.items()])}</ul>"
