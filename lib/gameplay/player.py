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
from typing import Union, TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from lib.gameplay.hex import ResourceType


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

    def longest_contiguous_road(self) -> int:
        raise NotImplementedError()

    def largest_army_size(self) -> int:
        return len(
            [
                card
                for card in self.development_cards
                if card.cardType == CardType.KNIGHT
            ]
        )

    def points(self, players: list["Player"]) -> int:
        # TODO: Add support for largest army and longest road
        return (
            reduce(lambda acc, curr: acc + curr.get_points(), self.cities, 0)
            + reduce(lambda acc, curr: acc + curr.get_points(), self.settlements, 0)
            + reduce(
                lambda acc, curr: acc + curr.get_points(), self.development_cards, 0
            )
        )

    def get_active_settlements(self) -> list[Settlement]:
        return [
            settlement
            for settlement in self.settlements
            if settlement.vertex is not None
        ]

    def get_unplaced_settlement(self) -> Union[Settlement, None]:
        for settlement in self.settlements:
            if settlement.position is None:
                return settlement
        return None

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

    def collect_resources(self, bank: Bank, dice_roll: int):
        for city in self.cities:
            if city.vertex is not None:
                for hex in city.vertex.hexes:
                    if hex.value == dice_roll and hex.resourceType is not None:
                        if hex.robber:
                            print(f"Robber blocked 2 {hex.resourceType} for {self}")
                        else:
                            print(f"{self} collected 2 {hex.resourceType}")
                            self.resources.append(bank.get_card(hex.resourceType))
                            self.resources.append(bank.get_card(hex.resourceType))
        for settlement in self.settlements:
            if settlement.vertex is not None:
                for hex in settlement.vertex.hexes:
                    if hex.value == dice_roll and hex.resourceType is not None:
                        if hex.robber:
                            print(f"Robber blocked {hex.resourceType} for {self}")
                        else:
                            print(f"{self} collected 1 {hex.resourceType}")
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

    def split_cards(self, bank: Bank):
        if len(self.resources) > 7:
            num_cards = len(self.resources) // 2
            for _ in range(num_cards):
                # TODO: Implement better logic for choosing which cards to return
                card = self.resources.pop()
                bank.return_card(card)

    def play_development_card(self, card: DevelopmentCard):
        pass

    def trade(
        self, other: "Player", offer: list[ResourceCard], request: list[ResourceCard]
    ):
        pass

    def trade_bank(self, offer: list[ResourceCard], request: list[ResourceCard]):
        pass

    def trade_port(self, offer: list[ResourceCard], request: list[ResourceCard]):
        pass

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

    def take_turn(self, board: Board, bank: Bank, players: list["Player"]):
        pass
