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

    # def pop_least_valuable_resource(self) -> "ResourceCard":
    #     raise NotImplementedError()

    def take_turn(self, board: "Board", bank: "Bank", players: list["Player"]) -> None:
        if self.can_build_city():
            current_settlments = self.current_settlements()
            logger.info(f"{self} building city at {current_settlments[0].position}")
            position = current_settlments[0].position
            if position is not None:
                self.build_city(board, position, bank)

        if self.can_build_settlement():
            possible_settlement_locs = board.possible_settlement_locations(self)
            if len(possible_settlement_locs) > 0:
                logger.info(
                    f"{self} building settlement at {possible_settlement_locs[0]}"
                )
                self.build_settlement(board, possible_settlement_locs[0], bank)

        resource_counts = self.resource_counts()
        for resource, count in resource_counts.items():
            while count >= 4:
                logger.info(f"{self} trading 4 {resource} for 1 {ResourceType.ORE}")
                try:
                    resources_to_return = self.take_resources_from_player(
                        [resource, resource, resource, resource]
                    )
                    for r in resources_to_return:
                        bank.return_card(r)
                    choice = random.choice([r for r in ResourceType if r != resource])

                    self.resources.append(bank.get_card(choice))
                    count -= 1
                except ValueError:
                    break

        if len(board.possible_settlement_locations(self)) > 3:
            return

        possible_road_locs = board.get_possible_road_locations(self)

        can_build_road = self.can_build_road()

        if len(possible_road_locs) > 0 and can_build_road:
            logger.info(f"{self} building road at {possible_road_locs[0]}")
            self.build_road(board, possible_road_locs[0].id, bank)
