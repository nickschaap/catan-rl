from lib.gameplay.bank import Bank
from lib.gameplay.board import Board
from lib.gameplay.player import Player
from lib.robot.action_type import ActionType
from lib.robot.action import Action
from typing import TYPE_CHECKING
import logging

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from lib.robot.action_graph import ActionGraph


class BuyDevelopmentCard(Action):
    def __init__(self, graph: "ActionGraph"):
        super().__init__(ActionType.BUY_DEVELOPMENT_CARD, graph)
        self.initialize_calculations()

    def calculate_cost(self) -> float:
        """Cost
        - The cost of the development card
        """
        return 3.0 * self.parameters["development_card_cost"]

    def calculate_reward(self) -> float:
        """Reward
        - To get another victory point
        - To get a knight to build up an army
        - To move the robber if you are being blocked

        """
        reward = 1.0
        robber_hex = self.board.hexes[self.board.robberLoc]
        player_state = self.player_state
        if self in robber_hex.get_settled_players():
            resource = robber_hex.resourceType
            if resource is not None:
                reward += 2.0 * player_state.resource_importance[resource]

        if len(self.player.resources) > 7:
            reward += 3.0

        return reward * self.parameters["development_card_reward"]

    def can_execute(self, board: Board, bank: Bank, player: Player) -> bool:
        return player.can_buy_development_card()

    def execute(
        self, board: Board, bank: Bank, player: Player, players: list[Player]
    ) -> None:
        logger.info(f"{player} buying development card")
        player.buy_development_card(bank)