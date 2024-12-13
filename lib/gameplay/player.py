from lib.gameplay.pieces import (
    Settlement,
    City,
    Road,
    ResourceCard,
    DevelopmentCard,
    CardType,
)
from lib.gameplay.bank import Bank
from lib.gameplay.board import Board
from functools import reduce
from lib.gameplay.hex import Hex
from lib.gameplay.pieces import PieceType
from typing import Union, Literal, TYPE_CHECKING
from lib.gameplay.hex import ResourceType
import logging
import random

if TYPE_CHECKING:
    from lib.gameplay.game import Game

logger = logging.getLogger(__name__)


def has_resources_or_can_trade(
    player: "Player", resources: list[ResourceType], bank: Bank
) -> bool:
    resource_counts = player.resource_counts().copy()

    needed_trades = []
    for resource in resources:
        if resource_counts[resource] > 0:
            resource_counts[resource] -= 1
        else:
            needed_trades.append(resource)

    for _ in needed_trades:
        trade_found = False
        for have_resource, count in resource_counts.items():
            if count >= bank.exchange_rate:
                resource_counts[have_resource] -= bank.exchange_rate
                trade_found = True
                break
        if not trade_found:
            return False

    return True


class Player:
    def __init__(self, id: int, color: str, game: "Game"):
        self.color = color
        self.id = id
        self.game = game

        self.cities: list[City] = []
        self.settlements: list[Settlement] = []
        self.roads: list[Road] = []
        self.resources: list[ResourceCard] = []
        self.development_cards: list[DevelopmentCard] = []

        self.setup_pieces()

    def __repr__(self):
        return f"Player {self.color}"

    def __hash__(self):
        return self.id

    def __eq__(self, value: "Player") -> bool:
        return isinstance(value, Player) and self.id == value.id

    def setup_pieces(self):
        self.cities = [City(self) for _ in range(4)]
        self.settlements = [Settlement(self) for _ in range(5)]
        self.roads = [Road(self) for _ in range(15)]

    def longest_contiguous_road(self, board: Board) -> int:
        return board.longest_road(self)

    def largest_army_size(self) -> int:
        return len(
            [
                card
                for card in self.development_cards
                if card.cardType == CardType.KNIGHT and card.flipped
            ]
        )

    def points(self) -> int:
        playerWithLongestRoad = self.game.player_with_longest_road
        playerWithLargestArmy = self.game.player_with_largest_army
        return (
            reduce(lambda acc, curr: acc + curr.get_points(), self.cities, 0)
            + reduce(lambda acc, curr: acc + curr.get_points(), self.settlements, 0)
            + reduce(
                lambda acc, curr: acc + curr.get_points(), self.development_cards, 0
            )
            + (2 if playerWithLongestRoad == self else 0)
            + (2 if playerWithLargestArmy == self else 0)
        )

    def give_development_card(self, card: DevelopmentCard) -> None:
        self.development_cards.append(card)

    def get_active_settlements(self) -> list[Settlement]:
        return [
            settlement
            for settlement in self.settlements
            if settlement.vertex is not None
        ]

    def num_active_settlements(self) -> int:
        return len(self.get_active_settlements())

    def get_active_cities(self) -> list[City]:
        return [city for city in self.cities if city.vertex is not None]

    def num_active_cities(self) -> int:
        return len(self.get_active_cities())

    def get_unplaced_settlement(self) -> Union[Settlement, None]:
        for settlement in self.settlements:
            if settlement.position is None:
                return settlement
        return None

    def unplaced_settlement_count(self) -> int:
        return len([s for s in self.settlements if s.position is None])

    def unplaced_city_count(self) -> int:
        return len([c for c in self.cities if c.position is None])

    def unplaced_road_count(self) -> int:
        return len([r for r in self.roads if r.position is None])

    def get_unplaced_city(self) -> Union[City, None]:
        for city in self.cities:
            if city.position is None:
                return city
        return None

    def get_unplaced_road(self) -> Union[Road, None]:
        for road in self.roads:
            if road.position is None:
                return road
        return None

    def get_active_roads(self) -> list[Road]:
        return [road for road in self.roads if road.position is not None]

    def collect_resources(self, bank: Bank, dice_roll: int):
        for city in self.cities:
            if city.vertex is not None:
                for hex in city.vertex.hexes:
                    if hex.value == dice_roll and hex.resourceType is not None:
                        if hex.robber:
                            logger.info(
                                f"Robber blocked 2 {hex.resourceType} for {self}"
                            )
                        else:
                            logger.info(f"{self} collected 2 {hex.resourceType}")
                            self.resources.append(bank.get_card(hex.resourceType))
                            self.resources.append(bank.get_card(hex.resourceType))
        for settlement in self.settlements:
            if settlement.vertex is not None:
                for hex in settlement.vertex.hexes:
                    if hex.value == dice_roll and hex.resourceType is not None:
                        if hex.robber:
                            logger.info(f"Robber blocked {hex.resourceType} for {self}")
                        else:
                            logger.info(f"{self} collected 1 {hex.resourceType}")
                            self.resources.append(bank.get_card(hex.resourceType))

    def pop_resource(self, resource: ResourceType) -> ResourceCard:
        for i, card in enumerate(self.resources):
            if card.resourceType == resource:
                return self.resources.pop(i)
        raise ValueError(f"Player does not have resource {resource}")

    def take_resources_from_player(
        self, resources: list["ResourceType"]
    ) -> list[ResourceCard]:
        cards: list[ResourceCard] = []
        resource_counts = self.resource_counts().copy()
        needed_resources = []

        # First handle exact matches
        for type in resources:
            if resource_counts[type] > 0:
                # Find and take the actual card
                cards.append(self.pop_resource(type))
                resource_counts[type] -= 1
            else:
                needed_resources.append(type)

        # Then handle remaining resources through trades
        exchange_rate = self.game.bank.exchange_rate
        if len(needed_resources) > 0:
            for needed_resource in needed_resources:
                # TODO: sort by importance
                for have_resource, count in resource_counts.items():
                    if count >= exchange_rate:
                        logger.info(
                            f"{self} attempting to finish transaction with {exchange_rate} {have_resource} for {needed_resource}"
                        )
                        # Execute the trade
                        trade_cards = []
                        for i, card in enumerate(self.resources):
                            if card.resourceType == have_resource:
                                trade_cards.append(self.resources.pop(i))
                                if len(trade_cards) == exchange_rate:
                                    break
                        cards.extend(trade_cards)
                        break
                else:  # No trade was possible
                    # Return all collected cards and raise error
                    self.resources.extend(cards)
                    raise ValueError(
                        f"Player does not have required resources and cannot trade for them. Needed {needed_resource}"
                    )
        return cards

    def give_resource_to_player(self, card: ResourceCard) -> None:
        self.resources.append(card)

    def get_settled_hexes(self) -> set[Hex]:
        settlements = self.get_active_settlements() + self.get_active_cities()

        settled_hexes = set()

        for settlement in settlements:
            if settlement.vertex is not None:
                settled_hexes.update(settlement.vertex.get_hexes())

        return settled_hexes

    def resource_counts(self) -> dict[ResourceType, int]:
        counts = {resource: 0 for resource in ResourceType}
        for card in self.resources:
            counts[card.resourceType] += 1
        return counts

    def resource_abundance(self) -> dict[ResourceType, float]:
        counts = {resource: 0.0 for resource in ResourceType}
        for settlement in self.get_active_settlements():
            for hex in list(
                settlement.vertex.hexes if settlement.vertex is not None else []
            ):
                if hex.resourceType is not None:
                    counts[hex.resourceType] += 1 * hex.likelihood()
        for city in self.get_active_cities():
            for hex in list(city.vertex.hexes if city.vertex is not None else []):
                if hex.resourceType is not None:
                    counts[hex.resourceType] += 2 * hex.likelihood()
        return counts

    def resource_importance(self) -> dict[ResourceType, float]:
        return {resource: 1 for resource in ResourceType}

    def purchase_power(
        self,
    ) -> dict[Union[PieceType, Literal["Development Card"]], int]:
        purchase_power = {}
        resource_abundance = self.resource_abundance()

        purchase_power[PieceType.SETTLEMENT] = (
            resource_abundance[ResourceType.BRICK]
            + resource_abundance[ResourceType.WOOD]
            + resource_abundance[ResourceType.WHEAT]
            + resource_abundance[ResourceType.SHEEP]
        ) / 4
        purchase_power[PieceType.CITY] = (
            resource_abundance[ResourceType.ORE] / 3
            + resource_abundance[ResourceType.WHEAT] / 2
        ) / 2
        purchase_power[PieceType.ROAD] = (
            resource_abundance[ResourceType.WOOD]
            + resource_abundance[ResourceType.BRICK]
        ) / 2
        purchase_power["Development Card"] = (
            resource_abundance[ResourceType.WHEAT]
            + resource_abundance[ResourceType.SHEEP]
            + resource_abundance[ResourceType.ORE]
        ) / 3
        return purchase_power

    def can_build_settlement(self) -> bool:
        return self.unplaced_settlement_count() > 0 and has_resources_or_can_trade(
            self,
            [
                ResourceType.BRICK,
                ResourceType.WOOD,
                ResourceType.WHEAT,
                ResourceType.SHEEP,
            ],
            self.game.bank,
        )

    def can_build_settlement_at_vertex(self, vertexLoc: int, board: "Board") -> bool:
        return (
            self.can_build_settlement()
            and board.vertices[vertexLoc].player_is_connected(self)
            and board.can_settle(vertexLoc)
        )

    def can_build_city(self) -> bool:
        return self.unplaced_city_count() > 0 and has_resources_or_can_trade(
            self,
            [
                ResourceType.ORE,
                ResourceType.ORE,
                ResourceType.ORE,
                ResourceType.WHEAT,
                ResourceType.WHEAT,
            ],
            self.game.bank,
        )

    def can_build_city_at_vertex(self, vertexLoc: int, board: "Board") -> bool:
        return self.can_build_city() and board.can_place_city(self, vertexLoc)

    def can_build_road(self) -> bool:
        return self.unplaced_road_count() > 0 and has_resources_or_can_trade(
            self,
            [ResourceType.BRICK, ResourceType.WOOD],
            self.game.bank,
        )

    def can_build_road_at_edge(self, edgeLoc: int, board: "Board") -> bool:
        return self.can_build_road() and board.edges[edgeLoc].player_is_connected(self)

    def pop_least_valuable_resource(self) -> Union[ResourceCard, None]:
        if len(self.resources) == 0:
            return None

        resource_rankings = self.rank_resource_values()
        resource_counts = self.resource_counts()

        for resource in resource_rankings:
            if resource_counts[resource] > 0:
                [card] = self.take_resources_from_player([resource])
                return card

    def split_cards(self, bank: Bank):
        if len(self.resources) > 7:
            num_cards = len(self.resources) // 2
            logger.info(f"Splitting cards for {self}, discarding {num_cards} cards")
            for _ in range(num_cards):
                card = self.pop_least_valuable_resource()
                if card is not None:
                    bank.return_card(card)
                else:
                    raise ValueError("No cards to split")

    def play_development_card(self, card: DevelopmentCard):
        pass

    def trade_bank(self, offer: list[ResourceType], request: ResourceType, bank: Bank):
        bank.return_cards(self.take_resources_from_player(offer))
        self.resources.append(bank.get_card(request))

    def build_settlement(self, board: Board, vertexLoc: int, bank: Bank):
        bank.purchase_settlement(self)
        board.place_settlement(self, vertexLoc)

    def build_city(self, board: Board, vertexLoc: int, bank: Bank):
        bank.purchase_city(self)
        board.place_city(self, vertexLoc)

    def build_road(self, board: Board, edgeLoc: int, bank: Bank):
        bank.purchase_road(self)
        board.place_road(self, edgeLoc)

    def buy_development_card(self, bank: Bank):
        self.development_cards.append(bank.purchase_dev_card(self))

    def can_buy_development_card(self) -> bool:
        resource_counts = self.resource_counts()
        return (
            resource_counts[ResourceType.ORE] >= 1
            and resource_counts[ResourceType.WHEAT] >= 1
            and resource_counts[ResourceType.SHEEP] >= 1
        )

    def get_hex_and_player_to_rob(
        self, board: Board, bank: Bank
    ) -> tuple[Hex, Union["Player", None]]:
        return random.choice(board.get_hexes()), None

    def rank_resource_values(self) -> list[ResourceType]:
        """Returns resources valuable to the player from most valuable to least valuable"""
        return [
            resource
            for resource, _ in sorted(
                self.resource_importance().items(), key=lambda x: x[1], reverse=False
            )
        ]

    def rob(self) -> Union[ResourceCard, None]:
        # Pop a random resource card from the player's resources
        if len(self.resources) == 0:
            return None

        card_index = random.randrange(len(self.resources))
        return self.resources.pop(card_index)

    def move_robber(self, board: Board, bank: Bank) -> None:
        hex, player_to_rob = self.get_hex_and_player_to_rob(board, bank)
        board.move_robber(hex.id)

        if player_to_rob is not None:
            card = player_to_rob.rob()
            if card is not None:
                self.resources.append(card)

    def pre_roll(self, board: Board, bank: Bank, players: list["Player"]) -> None:
        pass

    def take_turn(self, board: Board, bank: Bank, players: list["Player"]):
        pass
