from lib.gameplay.hex import ResourceType
from lib.gameplay.pieces import PieceType
from lib.robot.action_type import ActionType
from lib.robot.action import Action
from typing import TYPE_CHECKING
import logging
from lib.operations.ops import lerp, normalize

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
        self.resources_unlocks = self.resources_at_vertex()
        self.initialize_calculations()

    def calculate_cost(self) -> float:
        cost = 1 - self.player_state.purchase_power[PieceType.CITY]

        return normalize(self.parameters["city_building_cost"] * cost)

    def calculate_reward(self) -> float:
        """Reward
        - The resources at the vertex
        - Get access to more likely resources
        - To get another victory point
        """
        state = self.graph.player_state
        resource_importance = state.resource_importance
        # Sum of unlocked resources weighted by likelihood and importance
        reward = sum(resource_importance[r[0]] * r[1] for r in self.resources_unlocks)

        return normalize(self.parameters["city_building_reward"] * reward)

    def can_execute(self, board: "Board", bank: "Bank", player: "Player") -> bool:
        return player.can_build_city_at_vertex(self.vertex.id, board)

    def execute(
        self, board: "Board", bank: "Bank", player: "Player", players: list["Player"]
    ) -> None:
        logger.info(f"{player} building city at {self.vertex.id}")
        player.build_city(board, self.vertex.id, bank)
        self.executed = True

    def resources_at_vertex(self) -> list[tuple[ResourceType, float]]:
        return [
            (hex.resourceType, hex.likelihood())
            for hex in self.vertex.get_hexes()
            if hex.resourceType is not None
        ]

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
