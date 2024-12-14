from lib.gameplay.hex import ResourceType
from lib.gameplay.player import Player
from lib.robot.action_graph import ActionGraph
from typing import TYPE_CHECKING, Union
import logging

logger = logging.getLogger(__name__)

if TYPE_CHECKING:  # pragma: no cover
    from lib.gameplay.board import Board
    from lib.gameplay.bank import Bank
    from lib.gameplay.game import Game
    from lib.gameplay.hex import Hex


class Robot(Player):
    def __init__(self, id: int, color: str, game: "Game"):
        super().__init__(id, color, game)
        self.action_graph = ActionGraph(self, game)

    def get_hex_and_player_to_rob(
        self, board: "Board", bank: "Bank"
    ) -> tuple["Hex", Union["Player", None]]:
        # Get a sorted list of players by the number of points they have
        # and secondarily by the number of resources they have
        players = sorted(
            self.game.players,
            key=lambda p: (p.points(), len(p.resources)),
            reverse=True,
        )
        player_to_rob = next((p for p in players if p != self), None)
        if player_to_rob is None:
            return board.get_desert(), None

        robber_loc = board.robberLoc

        players_settled_hexes = [
            hex
            for hex in player_to_rob.get_settled_hexes()
            if hex.id != robber_loc and self not in hex.get_settled_players()
        ]

        # find the hex with the highest likelihood
        hex_to_rob = max(
            players_settled_hexes,
            key=lambda hex: hex.likelihood(),
        )

        return hex_to_rob, player_to_rob

    def resource_importance(self) -> dict[ResourceType, float]:
        resource_abundance = self.resource_abundance()

        importance = {
            resource: 1 - resource_abundance[resource] for resource in ResourceType
        }
        return importance

    def pre_roll(self, board: "Board", bank: "Bank", players: list["Player"]) -> None:
        self.action_graph.execute_actions("pre_roll")

    def take_turn(self, board: "Board", bank: "Bank", players: list["Player"]) -> None:
        # Go through the action graph and execute the actions
        self.action_graph.execute_actions("post_roll")
