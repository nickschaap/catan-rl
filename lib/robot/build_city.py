from lib.robot.action_type import ActionType
from lib.robot.action import Action
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from lib.robot.action_graph import ActionGraph
    from lib.gameplay.hex import Vertex


class BuildCity(Action):
    def __init__(self, vertex: "Vertex", graph: "ActionGraph"):
        super().__init__(ActionType.BUILD_CITY, graph)
        self.vertex = vertex

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
            "Priority": self.priority(),
        }
        return f"{self.action_type} ({self.vertex.id}) <ul>{''.join([f'<li>{k}: {v}</li>' for k, v in info.items()])}</ul>"
