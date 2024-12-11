from lib.robot.action_type import ActionType
from lib.robot.action import Action
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from lib.robot.action_graph import ActionGraph


class BuyDevelopmentCard(Action):
    def __init__(self, graph: "ActionGraph"):
        super().__init__(ActionType.BUY_DEVELOPMENT_CARD, graph)

    def __str__(self) -> str:
        return f"{self.action_type} <ul><li>Priority: {self.priority()}</li></ul>"
