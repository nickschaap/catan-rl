from lib.gameplay.bank import Bank
from lib.gameplay.board import Board
from lib.gameplay.pieces import CardType, DevelopmentCard
from lib.gameplay.player import Player
from lib.robot.action_type import ActionType
from lib.robot.action import Action
from typing import TYPE_CHECKING

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
        return 0 + self.parameters["play_development_card_cost_bias"]

    def calculate_reward(self) -> float:
        """Reward
        - To get another victory point
        - To get a knight to build up an army
        - To move the robber if you are being blocked

        """
        if self.card.cardType == CardType.KNIGHT:
            return 1.0
        elif self.card.cardType == CardType.VICTORY_POINT:
            return 100
        return 0.0

    def can_execute(self, board: Board, bank: Bank, player: Player) -> bool:
        return not self.card.flipped

    def execute(
        self, board: Board, bank: Bank, player: Player, players: list[Player]
    ) -> None:
        self.card.flip()

        if self.card.cardType == CardType.KNIGHT:
            player.move_robber(board, bank)
        elif self.card.cardType == CardType.VICTORY_POINT:
            # nothing to do
            pass
