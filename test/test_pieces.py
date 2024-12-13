import pytest

from lib.gameplay.pieces import (
    City,
    Road,
    Settlement,
    PieceType,
    DevelopmentCard,
    CardType,
    ResourceCard,
)
from lib.gameplay.hex import ResourceType
from lib.gameplay.player import Player
from lib.gameplay.board import Vertex, Board
from lib.gameplay.game import Game


@pytest.mark.pieces
def test_settlement() -> None:
    game = Game()
    settlement = Settlement(Player(0, "red", game))
    assert settlement.player.id == 0
    assert settlement.position is None

    settlement.set_vertex(None)
    assert settlement.position is None

    assert settlement.get_points() == 0

    settlement.set_vertex(Vertex(0))
    assert settlement.position is not None
    assert settlement.get_points() == 1

    assert settlement.type == PieceType.SETTLEMENT


@pytest.mark.pieces
def test_city() -> None:
    game = Game()
    city = City(Player(0, "red", game))
    assert city.player.id == 0
    assert city.position is None

    city.set_vertex(None)
    assert city.position is None

    assert city.get_points() == 0

    city.set_vertex(Vertex(0))
    assert city.position is not None
    assert city.get_points() == 2

    assert city.type == PieceType.CITY


@pytest.mark.pieces
def test_road() -> None:
    game = Game()
    road = Road(Player(0, "red", game))
    assert road.player.id == 0
    assert road.position is None

    road.set_position(0)
    assert road.position == 0

    assert road.type == PieceType.ROAD


@pytest.mark.pieces
def test_connecting_road() -> None:
    game = Game()
    board = Board()
    player = Player(0, "red", game)
    for loc in [1, 2, 7, 12, 13]:
        board.place_road(player, loc)

    def get_road_at_edge(edgeLoc: int) -> Road:
        for road in player.roads:
            if road.position == edgeLoc:
                return road
        raise ValueError("Road not found")  # pragma: no cover

    assert get_road_at_edge(7).get_num_branches(board) == 4

    connecting_roads = get_road_at_edge(7).get_connecting_roads(board)
    assert len(connecting_roads) == 4
    assert all([isinstance(road, Road) for road in connecting_roads])
    assert all([road.player == player for road in connecting_roads])


@pytest.mark.pieces
def test_development_card() -> None:
    dev_card = DevelopmentCard(CardType.KNIGHT)

    assert dev_card.get_type() == CardType.KNIGHT
    assert dev_card.get_points() == 0

    dev_card = DevelopmentCard(CardType.VICTORY_POINT)
    assert dev_card.get_type() == CardType.VICTORY_POINT
    assert dev_card.get_points() == 1


@pytest.mark.pieces
def test_resource_card() -> None:
    resource_card = ResourceCard(ResourceType.BRICK)
    assert resource_card.get_type() == ResourceType.BRICK
