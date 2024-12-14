from lib.gameplay.bank import Bank
from lib.gameplay.board import Board
from lib.gameplay.pieces import CardType, DevelopmentCard
from lib.gameplay.player import Player
from lib.operations.ops import normalize
from lib.robot.action_type import ActionType
from lib.robot.action import Action
from typing import TYPE_CHECKING
import logging

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from lib.robot.action_graph import ActionGraph


class PlayDevelopmentCard(Action):
    def __init__(self, card: DevelopmentCard, graph: "ActionGraph"):
        super().__init__(ActionType.PLAY_DEVELOPMENT_CARD, graph)
        self.card = card
        self.initialize_calculations()

    def calculate_cost(self) -> float:
        """Cost
        - The cost of the development card
        """
        return self.parameters["play_development_card_cost_bias"]

    def calculate_reward(self) -> float:
        """Reward
        - To get another victory point
        - To get a knight to build up an army
        - To move the robber if you are being blocked

        """
        reward = 0.0
        if self.card.cardType == CardType.KNIGHT:
            robber_hex = self.board.hexes[self.board.robberLoc]
            player_state = self.player_state
            if self in robber_hex.get_settled_players():
                resource = robber_hex.resourceType
                if resource is not None:
                    reward += player_state.resource_importance[resource]

            # If the player is close to getting largest army, play a knight
            reward += 1

        unflipped_knight_cards = [
            card
            for card in self.player_state.player.development_cards
            if card.cardType == CardType.KNIGHT and not card.flipped
        ]

        if len(unflipped_knight_cards) >= 1 or self.player.points() >= 7:
            reward += 1

        elif self.card.cardType == CardType.VICTORY_POINT:
            reward += 1.0
        return normalize(self.parameters["play_development_card_reward"] * reward)

    def can_execute(self, board: Board, bank: Bank, player: Player) -> bool:
        return not self.card.flipped

    def execute(
        self, board: Board, bank: Bank, player: Player, players: list[Player]
    ) -> None:
        logger.info(f"{player} playing development card {self.card.cardType}")
        self.card.flip()
        self.executed = True
        if self.card.cardType == CardType.KNIGHT:
            player.move_robber(board, bank)
        elif self.card.cardType == CardType.VICTORY_POINT:
            # nothing to do
            pass
