from lib.gameplay.params import DEFAULT_PARAMETERS, GameParameters
from lib.gameplay.pieces import ResourceCard, DevelopmentCard, CardType
from lib.gameplay.hex import ResourceType
from typing import TYPE_CHECKING, Union
import numpy as np
import random

if TYPE_CHECKING:  # pragma: no cover
    from lib.gameplay.player import Player


class Bank:
    def __init__(
        self,
        include_progress_cards: bool = True,
        parameters: GameParameters = DEFAULT_PARAMETERS,
    ):
        self.exchange_rate = parameters["bank_exchange_rate"]
        self.num_cards_per_resource = parameters["num_cards_per_resource"]
        self.brick_cards = [
            ResourceCard(ResourceType.BRICK) for _ in range(self.num_cards_per_resource)
        ]
        self.wood_cards = [
            ResourceCard(ResourceType.WOOD) for _ in range(self.num_cards_per_resource)
        ]
        self.sheep_cards = [
            ResourceCard(ResourceType.SHEEP) for _ in range(self.num_cards_per_resource)
        ]
        self.wheat_cards = [
            ResourceCard(ResourceType.WHEAT) for _ in range(self.num_cards_per_resource)
        ]
        self.ore_cards = [
            ResourceCard(ResourceType.ORE) for _ in range(self.num_cards_per_resource)
        ]

        self.dev_cards = [DevelopmentCard(CardType.KNIGHT) for _ in range(14)] + [
            DevelopmentCard(CardType.VICTORY_POINT) for _ in range(5)
        ]
        if include_progress_cards:
            self.dev_cards.extend(
                [DevelopmentCard(CardType.ROAD_BUILDING) for _ in range(2)]
                + [DevelopmentCard(CardType.MONOPOLY) for _ in range(2)]
                + [DevelopmentCard(CardType.YEAR_OF_PLENTY) for _ in range(2)]
            )
        random.shuffle(self.dev_cards)

    def get_cards(self, *resourceType: ResourceType) -> list[ResourceCard]:
        return [self.get_card(resource) for resource in resourceType]

    def get_card(self, resourceType: ResourceType) -> ResourceCard:
        try:
            if resourceType == ResourceType.BRICK:
                return self.brick_cards.pop()
            if resourceType == ResourceType.WOOD:
                return self.wood_cards.pop()
            if resourceType == ResourceType.SHEEP:
                return self.sheep_cards.pop()
            if resourceType == ResourceType.WHEAT:
                return self.wheat_cards.pop()
            if resourceType == ResourceType.ORE:
                return self.ore_cards.pop()
        except IndexError:
            raise ValueError(f"Bank ran out of {resourceType}")

    def get_dev_card(self, type: Union[CardType, None] = None) -> DevelopmentCard:
        if type is not None:
            # Find the next card of the passed in type
            def is_type(card: DevelopmentCard) -> bool:
                return card.get_type() == type

            index = next((i for i, v in enumerate(self.dev_cards) if is_type(v)), None)
            if index is None:
                raise ValueError(f"No {type} cards in the bank")
            return self.dev_cards.pop(index)
        # Default to a random card
        index = np.random.randint(0, len(self.dev_cards))
        return self.dev_cards.pop(index)

    def return_dev_card(self, card: DevelopmentCard) -> None:
        self.dev_cards.append(card)

    def return_card(self, card: ResourceCard) -> None:
        if card.resourceType == ResourceType.BRICK:
            self.brick_cards.append(card)
        if card.resourceType == ResourceType.WOOD:
            self.wood_cards.append(card)
        if card.resourceType == ResourceType.SHEEP:
            self.sheep_cards.append(card)
        if card.resourceType == ResourceType.WHEAT:
            self.wheat_cards.append(card)
        if card.resourceType == ResourceType.ORE:
            self.ore_cards.append(card)

    def resource_counts(self) -> dict[ResourceType, int]:
        return {
            ResourceType.BRICK: len(self.brick_cards),
            ResourceType.WOOD: len(self.wood_cards),
            ResourceType.SHEEP: len(self.sheep_cards),
            ResourceType.WHEAT: len(self.wheat_cards),
            ResourceType.ORE: len(self.ore_cards),
        }

    def return_cards(self, cards: list[ResourceCard]) -> None:
        for card in cards:
            self.return_card(card)

    def purchase_road(self, player: "Player"):
        cards = player.take_resources_from_player(
            [ResourceType.BRICK, ResourceType.WOOD]
        )
        for card in cards:
            self.return_card(card)

    def purchase_settlement(self, player: "Player"):
        cards = player.take_resources_from_player(
            [
                ResourceType.BRICK,
                ResourceType.WOOD,
                ResourceType.WHEAT,
                ResourceType.SHEEP,
            ]
        )
        for card in cards:
            self.return_card(card)

    def purchase_city(self, player: "Player"):
        cards = player.take_resources_from_player(
            [
                ResourceType.WHEAT,
                ResourceType.WHEAT,
                ResourceType.ORE,
                ResourceType.ORE,
                ResourceType.ORE,
            ]
        )
        for card in cards:
            self.return_card(card)

    def purchase_dev_card(self, player: "Player") -> DevelopmentCard:
        cards = player.take_resources_from_player(
            [ResourceType.WHEAT, ResourceType.SHEEP, ResourceType.ORE]
        )
        for card in cards:
            self.return_card(card)
        return self.get_dev_card()
