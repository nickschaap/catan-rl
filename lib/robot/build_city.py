from lib.robot.action_type import ActionType
from lib.robot.action import Action
from typing import TYPE_CHECKING
import logging

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from lib.robot.action_graph import ActionGraph
    from lib.gameplay.hex import Vertex
    from lib.gameplay.board import Board
    from lib.gameplay.bank import Bank
    from lib.gameplay.player import Player


class BuildCity(Action):
    def __init__(self, vertex: "Vertex", graph: "ActionGraph"):
        super().__init__(ActionType.BUILD_CITY, graph)
        self.vertex = vertex
        self.initialize_calculations()

    def calculate_cost(self) -> float:
        cost = 5.0

        # Add penalty if vertex is not on valuable resources
        resources = self.resources_at_vertex()
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
        return cost * self.parameters["city_building_cost"]

    def can_execute(self, board: "Board", bank: "Bank", player: "Player") -> bool:
        return player.can_build_city_at_vertex(self.vertex.id, board)

    def execute(
        self, board: "Board", bank: "Bank", player: "Player", players: list["Player"]
    ) -> None:
        logger.info(f"{player} building city at {self.vertex.id}")
        player.build_city(board, self.vertex.id, bank)

    def resources_at_vertex(self):
        return [
            hex.resourceType
            for hex in self.vertex.get_hexes()
            if hex.resourceType is not None
        ]

    def calculate_reward(self) -> float:
        """Reward
        - The resources at the vertex
        - Get access to more likely resources
        - To get another victory point
        """
        state = self.graph.player_state
        resources_at_hex = self.resources_at_vertex()
        resource_abundance = state.resource_abundance
        resource_importance = state.resource_importance

        reward = 0
        for resource in resources_at_hex:
            # Lower reward if we already have good access to this resource
            abundance_penalty = 1.0 / (1.0 + resource_abundance[resource])
            # Higher reward if this resource is important to us
            importance_multiplier = resource_importance[resource]
            reward += abundance_penalty * importance_multiplier
        return reward * self.parameters["city_building_reward"]

    def resources_at_hex(self) -> str:
        return ", ".join(
            [
                f"{hex.resourceType} ({hex.value})"
                for hex in self.vertex.get_hexes()
                if hex.resourceType is not None
            ]
        )

    def __str__(self) -> str:
        info = {
            "Resources at Hex": self.resources_at_hex(),
            "Priority": self.priority,
            "Cost": self.cost,
            "Reward": self.reward,
        }
        return f"{self.action_type} ({self.vertex.id}) <ul>{''.join([f'<li>{k}: {v}</li>' for k, v in info.items()])}</ul>"
