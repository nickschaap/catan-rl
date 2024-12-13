import pytest

from lib.gameplay.bank import Bank
from lib.gameplay.game import Game
from lib.gameplay.hex import ResourceType
from lib.gameplay.player import Player


@pytest.mark.bank
def test_bank() -> None:
    bank = Bank()

    assert len(bank.brick_cards) == 19
    assert len(bank.wood_cards) == 19
    assert len(bank.wheat_cards) == 19
    assert len(bank.sheep_cards) == 19
    assert len(bank.ore_cards) == 19

    assert len(bank.dev_cards) == 25

    for resource in ResourceType:
        card = bank.get_card(resource)
        assert card.get_type() == resource

        if resource == ResourceType.BRICK:
            assert len(bank.brick_cards) == 18
        elif resource == ResourceType.WOOD:
            assert len(bank.wood_cards) == 18
        elif resource == ResourceType.WHEAT:
            assert len(bank.wheat_cards) == 18
        elif resource == ResourceType.SHEEP:
            assert len(bank.sheep_cards) == 18
        elif resource == ResourceType.ORE:
            assert len(bank.ore_cards) == 18

        bank.return_card(card)

        if resource == ResourceType.BRICK:
            assert len(bank.brick_cards) == 19
        elif resource == ResourceType.WOOD:
            assert len(bank.wood_cards) == 19
        elif resource == ResourceType.WHEAT:
            assert len(bank.wheat_cards) == 19
        elif resource == ResourceType.SHEEP:
            assert len(bank.sheep_cards) == 19
        elif resource == ResourceType.ORE:
            assert len(bank.ore_cards) == 19

    dev_card = bank.get_dev_card()

    assert len(bank.dev_cards) == 24

    bank.return_dev_card(dev_card)

    assert len(bank.dev_cards) == 25


@pytest.mark.bank
def test_buy_settlement() -> None:
    bank = Bank()
    player = Player(1, "red", Game())

    player.resources = bank.get_cards(ResourceType.BRICK, ResourceType.WOOD)

    with pytest.raises(ValueError):
        bank.purchase_settlement(player)

    assert len(player.resources) == 2
    assert len(bank.brick_cards) == 18
    assert len(bank.wood_cards) == 18

    player.resources.extend(bank.get_cards(ResourceType.WHEAT, ResourceType.SHEEP))

    assert len(bank.wheat_cards) == 18
    assert len(bank.sheep_cards) == 18

    bank.purchase_settlement(player)
    assert len(player.resources) == 0
    assert len(bank.wheat_cards) == 19
    assert len(bank.sheep_cards) == 19
    assert len(bank.brick_cards) == 19
    assert len(bank.wood_cards) == 19


@pytest.mark.bank
def test_buy_road() -> None:
    bank = Bank()
    player = Player(1, "red", Game())

    player.resources = bank.get_cards(ResourceType.BRICK)

    with pytest.raises(ValueError):
        bank.purchase_road(player)

    assert len(player.resources) == 1

    player.resources.extend(bank.get_cards(ResourceType.WOOD))

    bank.purchase_road(player)

    assert len(player.resources) == 0
    assert len(bank.brick_cards) == 19
    assert len(bank.wood_cards) == 19


@pytest.mark.bank
def test_buy_city() -> None:
    game = Game()
    bank = game.bank
    player = game.players[0]

    resource_counts = player.resource_counts()

    assert resource_counts[ResourceType.WOOD] == 2
    assert resource_counts[ResourceType.WHEAT] == 1

    initial_bank_wheat = len(bank.wheat_cards)
    initial_bank_ore = len(bank.ore_cards)

    with pytest.raises(ValueError):
        bank.purchase_city(player)

    assert len(bank.wheat_cards) == initial_bank_wheat
    assert len(bank.ore_cards) == initial_bank_ore

    assert len(player.resources) == 3

    player.resources.extend(
        bank.get_cards(
            ResourceType.WHEAT, ResourceType.ORE, ResourceType.ORE, ResourceType.ORE
        )
    )

    assert player.resource_counts()[ResourceType.ORE] == 3
    assert player.resource_counts()[ResourceType.WHEAT] == 2

    assert len(player.resources) == 7
    assert player.can_build_city()

    initial_bank_wheat = len(bank.wheat_cards)
    initial_bank_ore = len(bank.ore_cards)

    bank.purchase_city(player)

    assert player.resource_counts()[ResourceType.ORE] == 0
    assert player.resource_counts()[ResourceType.WHEAT] == 0
    assert player.resource_counts()[ResourceType.WOOD] == 2

    assert len(player.resources) == 2
    assert len(bank.wheat_cards) == initial_bank_wheat + 2
    assert len(bank.ore_cards) == initial_bank_ore + 3


@pytest.mark.bank
def test_buy_dev_card() -> None:
    bank = Bank()
    player = Player(1, "red", Game())

    player.resources = bank.get_cards(ResourceType.ORE)

    with pytest.raises(ValueError):
        bank.purchase_dev_card(player)

    assert len(player.resources) == 1

    player.resources.extend(bank.get_cards(ResourceType.WHEAT, ResourceType.SHEEP))

    bank.purchase_dev_card(player)

    assert len(player.resources) == 0
    assert len(bank.sheep_cards) == 19
    assert len(bank.wheat_cards) == 19
    assert len(bank.ore_cards) == 19
    assert len(bank.dev_cards) == 24
