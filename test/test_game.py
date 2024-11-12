import pytest
from lib.gameplay.game import Game
from lib.gameplay.bank import Bank
from lib.gameplay.board import Board
from lib.gameplay.dice import Dice
from lib.gameplay.player import Player
from lib.gameplay.hex import ResourceType
import copy


class FakeDice(Dice):
    def __init__(self):
        super().__init__()
        self.dice = [0, 0]

    def roll(self) -> int:
        return self.get_sum()

    def get_sum(self) -> int:
        return sum(self.dice)

    def set_roll(self, *roll: int) -> None:
        self.dice = list(roll)
        self.total = self.get_sum()


def player_has_exact_resources(player: Player, resources: list[ResourceType]) -> bool:
    player_resources = copy.deepcopy(player.resources)
    for resource in resources:
        for card in player_resources:
            if card.resourceType == resource:
                player_resources.remove(card)
                break
    return player_resources == []


@pytest.mark.game
def test_game() -> None:
    game = Game()

    assert game.current_player == 0
    assert game.winning_player is None
    assert isinstance(game.bank, Bank)
    assert isinstance(game.board, Board)
    assert len(game.players) == 4

    assert game.get_current_player() == game.players[0]
    assert game.get_current_player().id == game.current_player

    assert game.get_player_by_color("red") == game.players[0]
    assert game.get_player_by_color("blue") == game.players[1]
    assert game.get_player_by_color("white") == game.players[2]
    assert game.get_player_by_color("orange") == game.players[3]
    with pytest.raises(ValueError):
        game.get_player_by_color("green")

    assert player_has_exact_resources(
        game.get_player_by_color("red"),
        [
            ResourceType.WHEAT,
            ResourceType.WOOD,
            ResourceType.WOOD,
        ],
    )

    assert player_has_exact_resources(
        game.get_player_by_color("blue"),
        [
            ResourceType.WOOD,
            ResourceType.ORE,
            ResourceType.BRICK,
        ],
    )

    assert player_has_exact_resources(
        game.get_player_by_color("white"),
        [
            ResourceType.WHEAT,
            ResourceType.WOOD,
            ResourceType.BRICK,
        ],
    )

    assert player_has_exact_resources(
        game.get_player_by_color("orange"),
        [
            ResourceType.WHEAT,
            ResourceType.WHEAT,
            ResourceType.ORE,
        ],
    )

    dice = FakeDice()
    game.dice = dice

    dice.set_roll(3, 3)

    game.step()

    assert player_has_exact_resources(
        game.get_player_by_color("red"),
        [
            ResourceType.WHEAT,
            ResourceType.WOOD,
            ResourceType.WOOD,
            ResourceType.BRICK,
        ],
    )

    assert player_has_exact_resources(
        game.get_player_by_color("blue"),
        [
            ResourceType.WOOD,
            ResourceType.ORE,
            ResourceType.BRICK,
        ],
    )

    assert player_has_exact_resources(
        game.get_player_by_color("white"),
        [ResourceType.WHEAT, ResourceType.WOOD, ResourceType.BRICK, ResourceType.BRICK],
    )

    game.board.move_robber(4)

    assert game.current_player == 1

    game.step()

    assert player_has_exact_resources(
        game.get_player_by_color("red"),
        [
            ResourceType.WHEAT,
            ResourceType.WOOD,
            ResourceType.WOOD,
            ResourceType.BRICK,
        ],
    )
