import pytest

from lib.gameplay.game import Game
from lib.gameplay.hex import ResourceType
from lib.gameplay.player import has_resources_or_can_trade


@pytest.mark.player
def test_player() -> None:
    game = Game()
    player = game.players[0]

    assert player.id == 0
    assert player.color == "red"
    assert str(player) == "Player red"
    assert hash(player) == 0

    assert len(player.cities) == 4
    assert len(player.settlements) == 5
    assert len(player.roads) == 15

    assert player.largest_army_size() == 0
    assert player.longest_contiguous_road(game.board) == 1
    assert player.points() == 2

    settled_hexes = player.get_settled_hexes()
    assert len(settled_hexes) == 6
    assert game.board.hexes[0] in settled_hexes
    assert game.board.hexes[1] in settled_hexes
    assert game.board.hexes[4] in settled_hexes
    assert game.board.hexes[7] in settled_hexes
    assert game.board.hexes[8] in settled_hexes
    assert game.board.hexes[12] in settled_hexes


def test_has_resources_or_can_trade() -> None:
    game = Game()
    player = game.players[0]
    bank = game.bank

    assert has_resources_or_can_trade(
        player, [ResourceType.WHEAT, ResourceType.WOOD], bank
    )

    assert not has_resources_or_can_trade(
        player, [ResourceType.WHEAT, ResourceType.WOOD, ResourceType.ORE], bank
    )

    player.resources = player.resources + bank.get_cards(
        ResourceType.WHEAT, ResourceType.WHEAT, ResourceType.WHEAT
    )

    assert player.resource_counts()[ResourceType.WHEAT] == 4

    assert has_resources_or_can_trade(
        player, [ResourceType.WOOD, ResourceType.ORE], bank
    )


def test_take_resources_from_player() -> None:
    game = Game()
    player = game.players[0]
    bank = game.bank
    player.resources = player.resources + bank.get_cards(
        ResourceType.WHEAT, ResourceType.WHEAT, ResourceType.WHEAT
    )

    player.take_resources_from_player([ResourceType.WOOD, ResourceType.ORE])

    resource_counts = player.resource_counts()

    assert resource_counts[ResourceType.WHEAT] == 4 - bank.exchange_rate
    assert resource_counts[ResourceType.WOOD] == 1
    assert resource_counts[ResourceType.ORE] == 0
