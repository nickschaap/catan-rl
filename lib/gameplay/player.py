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
from typing import Union
from lib.gameplay.hex import ResourceType
import logging
import random

logger = logging.getLogger(__name__)


class Player:
    def __init__(self, id: int, color: str):
        self.color = color
        self.id = id

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
                if card.cardType == CardType.KNIGHT
            ]
        )

    def points(
        self,
        playerWithLongestRoad: Union["Player", None],
        playerWithLargestArmy: Union["Player", None],
    ) -> int:
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

    def take_resources_from_player(
        self, resources: list["ResourceType"]
    ) -> list[ResourceCard]:
        cards: list[ResourceCard] = []
        for type in resources:
            found = False
            for i, card in enumerate(self.resources):
                if card.resourceType == type:
                    cards.append(self.resources.pop(i))
                    found = True
                    break
            if not found:
                self.resources.extend(cards)
                raise ValueError("Player does not have required resources")
        return cards

    def give_resource_to_player(self, card: ResourceCard) -> None:
        self.resources.append(card)

    def resource_counts(self) -> dict[ResourceType, int]:
        counts = {resource: 0 for resource in ResourceType}
        for card in self.resources:
            counts[card.resourceType] += 1
        return counts

    def resource_abundance(self) -> dict[ResourceType, int]:
        counts = {resource: 0 for resource in ResourceType}
        for settlement in self.get_active_settlements():
            for hex in settlement.vertex.hexes:
                if hex.resourceType is not None:
                    counts[hex.resourceType] += 1 * hex.likelihood()
        for city in self.get_active_cities():
            for hex in city.vertex.hexes:
                if hex.resourceType is not None:
                    counts[hex.resourceType] += 2 * hex.likelihood()
        return counts

    def can_build_settlement(self) -> bool:
        resource_counts = self.resource_counts()
        return (
            self.unplaced_settlement_count() > 0
            and resource_counts[ResourceType.BRICK] >= 1
            and resource_counts[ResourceType.WOOD] >= 1
            and resource_counts[ResourceType.WHEAT] >= 1
            and resource_counts[ResourceType.SHEEP] >= 1
        )

    def can_build_city(self) -> bool:
        resource_counts = self.resource_counts()
        return (
            self.unplaced_city_count() > 0
            and len(self.get_active_cities()) > 0
            and resource_counts[ResourceType.WHEAT] >= 2
            and resource_counts[ResourceType.ORE] >= 3
        )

    def can_build_road(self) -> bool:
        resource_counts = self.resource_counts()
        return (
            self.unplaced_road_count() > 0
            and resource_counts[ResourceType.BRICK] >= 1
            and resource_counts[ResourceType.WOOD] >= 1
        )

    def pop_least_valuable_resource(self) -> Union[ResourceCard, None]:
        if len(self.resources) == 0:
            return None

        resource_rankings = reversed(self.rank_resource_values())
        resource_counts = self.resource_counts()

        for resource in resource_rankings:
            if resource_counts[resource] > 0:
                [card] = self.take_resources_from_player([resource])
                return card

    def split_cards(self, bank: Bank):
        if len(self.resources) > 7:
            num_cards = len(self.resources) // 2
            for _ in range(num_cards):
                bank.return_card(self.pop_least_valuable_resource())

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
        bank.purchase_dev_card(self)

    def get_hex_to_rob(self, board: Board, bank: Bank) -> Hex:
        return random.choice(board.get_hexes())

    def choose_player_to_rob(
        self, players: list["Player"], board: Board, bank: Bank
    ) -> Union["Player", None]:
        return None if len(players) == 0 else players[0]

    def rank_resource_values(self) -> list[ResourceType]:
        """Returns resources valuable to the player from most valuable to least valuable"""
        return [
            ResourceType.ORE,
            ResourceType.BRICK,
            ResourceType.SHEEP,
            ResourceType.WHEAT,
            ResourceType.WOOD,
        ]

    def rob(self) -> Union[ResourceCard, None]:
        return self.pop_least_valuable_resource()

    def move_robber(self, board: Board, bank: Bank) -> None:
        hex = self.get_hex_to_rob(board, bank)
        board.move_robber(hex.id)

        settled_players = hex.get_settled_players()
        player_to_rob = self.choose_player_to_rob(settled_players, board, bank)
        if player_to_rob is not None:
            player_to_rob.rob()

    def take_turn(self, board: Board, bank: Bank, players: list["Player"]):
        pass
