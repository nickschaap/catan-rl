from lib.gameplay.player import Player
from lib.gameplay.hex import ResourceType
from typing import TYPE_CHECKING
import random
import logging

logger = logging.getLogger(__name__)

if TYPE_CHECKING:  # pragma: no cover
    from lib.gameplay.board import Board
    from lib.gameplay.bank import Bank


class Robot(Player):
    def __init__(self, id: int, color: str):
        super().__init__(id, color)

    def rank_resource_values(self) -> list[ResourceType]:
        """Returns resources valuable to the player from most valuable to least valuable"""
        resource_availability = {resource: 0 for resource in ResourceType}
        active_cities = self.get_active_cities()
        active_settlements = self.get_active_settlements()

        for city in active_cities:
            for hex in city.vertex.hexes:
                if hex.resourceType is not None:
                    resource_availability[hex.resourceType] += 2 * hex.likelihood()
        for settlement in active_settlements:
            for hex in settlement.vertex.hexes:
                if hex.resourceType is not None:
                    resource_availability[hex.resourceType] += 1 * hex.likelihood()

        # Lowest resource availability is highest value
        return sorted(resource_availability, key=lambda k: resource_availability[k])

    def take_turn(self, board: "Board", bank: "Bank", players: list["Player"]) -> None:
        # Check if the player can build a city
        if self.can_build_city():
            current_settlments = self.current_settlements()
            logger.info(f"{self} building city at {current_settlments[0].position}")
            position = current_settlments[0].position
            if position is not None:
                self.build_city(board, position, bank)

        # Check if the player can build a settlement
        if self.can_build_settlement():
            possible_settlement_locs = board.possible_settlement_locations(self)
            if len(possible_settlement_locs) > 0:
                logger.info(
                    f"{self} building settlement at {possible_settlement_locs[0]}"
                )
                self.build_settlement(board, possible_settlement_locs[0], bank)

        resource_counts = self.resource_counts()
        for resource, count in resource_counts.items():
            while count >= 4 and resource != ResourceType.ORE:
                # Try to trade the bank for a random resource
                random_resource = random.choice(
                    [r for r in ResourceType if r != resource]
                )
                logger.info(f"{self} trading 4 {resource} for 1 {random_resource}")
                self.trade_bank(
                    [resource] * 4,
                    random_resource,
                    bank,
                )
                count -= 4

        if len(board.possible_settlement_locations(self)) > 3:
            return

        # If there isn't enough settlement possibilities build roads
        possible_road_locs = board.get_possible_road_locations(self)

        can_build_road = self.can_build_road()

        if len(possible_road_locs) > 0 and can_build_road:
            logger.info(f"{self} building road at {possible_road_locs[0]}")
            # Always chooses the first possible road location
            self.build_road(board, possible_road_locs[0].id, bank)
