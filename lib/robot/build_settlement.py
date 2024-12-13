from lib.robot.action_type import ActionType
from lib.robot.action import Action
from typing import TYPE_CHECKING, Union

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
        # Base cost for building a settlement
        cost = 4.0  # Represents resource cost (wheat + wood + brick + sheep)

        if self.road_path is None:
            cost *= 1000
            return cost * self.parameters["settlement_building_cost"]

        # Add distance penalty based on how far we need to build roads to reach this vertex
        if len(self.road_path) > 0:
            # Each road we need to build adds to the cost
            # Cost is exponential to prefer closer settlements
            cost += 2.0 * (2 ** len(self.road_path))

        # Check if we have the required resources
        can_build = self.player.can_build_settlement()

        if not can_build:
            # Heavy penalty if we don't have required resources
            cost *= 2.0

        # Add penalty if vertex is not on valuable resources
        resources = self.resource_unlocks
        state = self.graph.player_state
        resource_importance = state.resource_importance

        if len(resources) == 0:
            cost *= 1.5
        else:
            # Calculate average importance of resources at this vertex
            avg_importance = sum(resource_importance[r] for r in resources) / len(
                resources
            )
            # Add penalty for low-importance resources (max penalty of 1.5x)
            importance_penalty = 1.5 - min(avg_importance, 1.0)
            cost *= 1.0 + importance_penalty

        return cost * self.parameters["settlement_building_cost"]

    def calculate_reward(self) -> float:
        """Reward
        - The resources at the vertex
        - Get access to more likely resources
        - To get another victory point
        """
        state = self.graph.player_state
        resources_at_hex = self.resource_unlocks
        resource_abundance = state.resource_abundance
        resource_importance = state.resource_importance

        reward = 0
        for resource in resources_at_hex:
            # Lower reward if we already have good access to this resource
            abundance_penalty = 1.0 / (1.0 + resource_abundance[resource])
            # Higher reward if this resource is important to us
            importance_multiplier = resource_importance[resource]
            reward += abundance_penalty * importance_multiplier
        return reward * self.parameters["settlement_building_reward"]

    def min_distance_to_road(self) -> Union[list["Edge"], None]:
        path = self.board.shortest_path(self.player, self.vertex.id)
        if path is None:
            return None
        return [edge for edge in path]

    def resources_at_vertex(self):
        return [
            hex.resourceType
            for hex in self.vertex.get_hexes()
            if hex.resourceType is not None
        ]

    def can_execute(self, board: "Board", bank: "Bank", player: "Player") -> bool:
        return player.can_build_settlement_at_vertex(self.vertex.id, board)

    def execute(
        self, board: "Board", bank: "Bank", player: "Player", players: list["Player"]
    ) -> None:
        player.build_settlement(board, self.vertex.id, bank)

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
