import pytest
from lib.gameplay.game import Game
from lib.gameplay.bank import Bank
from lib.gameplay.board import Board
from lib.gameplay.dice import Dice
from lib.gameplay.player import Player
from lib.gameplay.hex import ResourceType
from lib.gameplay.pieces import CardType
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


def test_longest_road() -> None:
    game = Game()

    assert game.get_player_with_largest_army() is None
    assert game.get_player_with_longest_road() is None

    board = game.board
    player1 = game.players[0]
    for edge in [0, 1, 2, 3, 4]:
        board.place_road(player1, edge)
        if edge <= 3:
            assert game.get_player_with_longest_road() is None
        else:
            assert game.get_player_with_longest_road() == player1

    player2 = game.players[1]
    board.place_road(player2, 5)
    assert game.get_player_with_longest_road() == player1

    for edge in [9, 17, 22, 32, 38]:
        board.place_road(player2, edge)
        if edge != 38:
            assert game.get_player_with_longest_road() == player1
        else:
            assert game.get_player_with_longest_road() == player2


def test_largest_army() -> None:
    game = Game()
    bank = game.bank

    assert game.get_player_with_largest_army() is None
    player1 = game.players[0]
    for i in range(3):
        card = bank.get_dev_card(type=CardType.KNIGHT)
        card.flip()
        player1.give_development_card(card)
        if i < 2:
            assert game.get_player_with_largest_army() is None
    assert game.get_player_with_largest_army() == player1

    player2 = game.players[1]
    for i in range(4):
        card = bank.get_dev_card(type=CardType.KNIGHT)
        card.flip()
        player2.give_development_card(card)
        if i < 3:
            assert game.get_player_with_largest_army() == player1
    assert game.get_player_with_largest_army() == player2


def test_connected_edges() -> None:
    game = Game()
    board = game.board
    player1 = game.players[0]

    connected_edges = board.edges[13].connected_edges(player1)
    assert set(connected_edges) == {
        board.edges[20],
        board.edges[14],
        board.edges[7],
        board.edges[12],
    }


def test_can_settle() -> None:
    game = Game()
    board = game.board

    for vertex in [0, 1, 8]:
        assert board.can_settle(vertex)

    for vertex in [10, 19]:
        assert not board.can_settle(vertex)


def test_rob() -> None:
    game = Game()

    player1 = game.players[0]

    resource_counts = player1.resource_counts()
    assert resource_counts[ResourceType.WOOD] == 2
    assert resource_counts[ResourceType.WHEAT] == 1

    for _ in range(3):
        card = player1.rob()
        assert card is not None
        assert (
            card.get_type() == ResourceType.WOOD
            or card.get_type() == ResourceType.WHEAT
        )

    resource_counts = player1.resource_counts()
    assert all(resource_counts[resource] == 0 for resource in ResourceType)

    card = player1.rob()
    assert card is None


def test_branch_vertices() -> None:
    game = Game()
    board = game.board
    player = game.players[0]

    branch_vertices = board.get_possible_branch_vertices(player)
    assert len(branch_vertices) == 4
    assert 10 in branch_vertices
    assert 11 in branch_vertices
    assert 29 in branch_vertices
    assert 30 in branch_vertices


def test_player_is_connected() -> None:
    game = Game()
    board = game.board
    player = game.players[0]

    for edge in [12, 7, 14, 20, 34, 40, 50, 42]:
        assert board.edges[edge].player_is_connected(player)

    for edge in [67, 61, 5, 0]:
        assert not board.edges[edge].player_is_connected(player)

    for vertex in [10, 29, 11, 30]:
        assert board.vertices[vertex].player_is_connected(player)

    for vertex in [19, 38]:
        assert not board.vertices[vertex].player_is_connected(player)


def test_can_place_city() -> None:
    game = Game()
    board = game.board
    player = game.players[0]

    assert board.can_place_city(player, 10)
    assert board.can_place_city(player, 29)

    assert not board.can_place_city(player, 19)
    assert not board.can_place_city(player, 38)
