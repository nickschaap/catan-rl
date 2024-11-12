import pytest

from lib.gameplay.board import Board
from lib.gameplay.player import Player
from lib.gameplay.pieces import PieceType
import random


@pytest.mark.board
def test_board() -> None:
    board = Board()

    assert len(board.get_hexes()) == 19
    assert len(board.edges) == 72
    assert len(board.vertices) == 54

    assert board.robberLoc == 9

    player = Player(1, "red")
    player2 = Player(2, "blue")

    board.place_settlement(player, 1)

    with pytest.raises(ValueError):
        board.place_city(player, 2)

    with pytest.raises(ValueError):
        board.place_city(player2, 1)

    with pytest.raises(ValueError):
        board.place_settlement(player2, 1)

    player2.settlements = []

    with pytest.raises(ValueError):
        board.place_settlement(player2, 2)

    assert len(board.get_settlements()) == 1

    board.place_city(player, 1)

    player.cities = []

    with pytest.raises(ValueError):
        board.place_city(player, 1)

    assert len(board.get_settlements()) == 1

    vertex = board.get_settlements()[0]

    assert vertex.piece is not None
    assert vertex.piece.type == PieceType.CITY

    board.place_road(player, 1)

    assert len(board.get_roads()) == 1

    with pytest.raises(ValueError):
        board.place_road(player, 1)

    player.roads = []

    with pytest.raises(ValueError):
        board.place_road(player, 2)

    assert len(board.move_robber(3)) == 0
    assert board.robberLoc == 3


@pytest.mark.board
def test_traverse() -> None:
    board = Board()

    hex = board.hexes[0]
    assert hex.edges[1].north_neighbor() == hex.vertices[0]
    assert hex.edges[1].south_neighbor() == hex.vertices[2]

    assert hex.edges[3].north_neighbor() == hex.vertices[2]
    assert hex.edges[3].south_neighbor() == hex.vertices[4]

    assert hex.edges[5].north_neighbor() == hex.vertices[4]
    assert hex.edges[5].south_neighbor() == hex.vertices[6]

    assert hex.edges[11].north_neighbor() == hex.vertices[0]
    assert hex.edges[11].south_neighbor() == hex.vertices[10]

    hex1 = board.hexes[1]
    assert hex1.edges[9].north_neighbor() == hex.vertices[2]
    assert hex1.edges[9].south_neighbor() == hex.vertices[4]

    vertex = hex.vertices[2]
    assert len(vertex.connected_edges()) == 3
    assert hex.edges[3] in vertex.connected_edges()
    assert hex1.edges[9] in vertex.connected_edges()
    assert hex1.edges[11] in vertex.connected_edges()
    assert hex.edges[1] in vertex.connected_edges()

    for i in range(1, 12, 2):
        assert len(hex.edges[i].vertices()) == 2


@pytest.mark.board
def test_longest_road() -> None:
    def setup_road(*edgeLocs: int) -> int:
        board = Board()
        player = Player(1, "red")
        random.shuffle(player.roads)
        for edgeLoc in edgeLocs:
            board.place_road(player, edgeLoc)

        return board.longest_road(player)

    assert setup_road(0, 1, 2, 3, 4, 5, 7) == 6
    assert setup_road() == 0
    # Circle around hex
    assert setup_road(0, 1, 7, 12, 11, 6) == 6

    assert setup_road(0, 1, 2, 3, 4, 5, 7, 12, 11) == 7

    assert setup_road(21, 15, 16, 29, 30) == 3

    # Figure 8
    assert setup_road(12, 13, 20, 27, 26, 19, 14, 15, 21, 29, 28) == 11

    # disconnected road
    assert setup_road(0, 1, 2, 3, 4, 5, 7, 60, 61, 62) == 6
    assert setup_road(60, 61, 53) == 3


@pytest.mark.board
def test_longest_road_multiplayer() -> None:
    def setup_board(options: dict[str, list[int]]) -> tuple[Board, Player, Player]:
        player1, player2 = Player(1, "red"), Player(2, "blue")
        players = {"1": player1, "2": player2}
        board = Board()
        for player, edgeLocs in options.items():
            for edgeLoc in edgeLocs:
                board.place_road(players[player], edgeLoc)
        return board, player1, player2

    board, player1, player2 = setup_board({"1": [0, 1, 2, 3, 4, 5, 7]})
    assert board.longest_road(player1) == 6
    assert board.longest_road(player2) == 0

    board, player1, player2 = setup_board(
        {"1": [0, 1, 2, 3, 4, 5, 7], "2": [25, 26, 27]}
    )
    assert board.longest_road(player1) == 6
    assert board.longest_road(player2) == 3

    board, player1, player2 = setup_board({"1": [0, 1, 2, 3, 4, 5, 7]})
    board.place_settlement(player2, 4)
    assert board.longest_road(player1) == 4
    assert board.longest_road(player2) == 0


@pytest.mark.board
def test_can_settle() -> None:
    def setup_board() -> tuple[Board, Player, Player]:
        player1, player2 = Player(1, "red"), Player(2, "blue")
        board = Board()
        return board, player1, player2

    board, player1, player2 = setup_board()
    board.place_settlement(player1, 1)

    assert board.can_settle(2) is False
    assert board.can_settle(0) is False
    assert board.can_settle(10) is True
    assert board.can_settle(8) is True

    with pytest.raises(ValueError):
        board.place_settlement(player2, 2)

    board.place_settlement(player2, 22)

    for loc in [21, 23, 33]:
        assert board.can_settle(loc) is False
    for loc in [20, 31, 52, 34, 24]:
        assert board.can_settle(loc) is True

    with pytest.raises(ValueError):
        board.place_settlement(player1, 1)

    with pytest.raises(ValueError):
        board.place_city(player2, 1)


@pytest.mark.board
def test_possible_settlements() -> None:
    def setup_board(*roads: int) -> tuple[Board, Player]:
        player1 = Player(1, "red")
        board = Board()
        for road in roads:
            board.place_road(player1, road)
        return board, player1

    board, player1 = setup_board(0, 1, 2, 3, 4, 5, 7)
    assert sorted(board.possible_settlement_locations(player1)) == sorted(
        [0, 1, 2, 10, 3, 4, 5, 6]
    )

    board, player1 = setup_board(0, 1, 7, 12, 11, 6)
    board.place_settlement(player1, 0)
    assert sorted(board.possible_settlement_locations(player1)) == sorted([2, 9, 10])


@pytest.mark.board
def test_can_player_settle() -> None:
    def setup_board(*roads: int) -> tuple[Board, Player, Player]:
        player1, player2 = Player(1, "red"), Player(2, "blue")
        board = Board()
        for road in roads:
            board.place_road(player1, road)
        return board, player1, player2

    board, player1, player2 = setup_board(0, 1, 2, 3, 4, 5, 7)
    for loc in [0, 1, 2, 3, 4, 5, 6, 10]:
        assert board.can_player_settle(player1, loc) is True
    for loc in [0, 1, 3, 4, 5, 6, 7, 8, 9, 10]:
        assert board.can_player_settle(player2, loc) is False


@pytest.mark.board
def test_move_robber() -> None:
    def setup_board(*roads: int) -> tuple[Board, Player]:
        player1 = Player(1, "red")
        board = Board()
        for road in roads:
            board.place_road(player1, road)
        return board, player1

    board, player1 = setup_board(0, 1, 2, 3, 4, 5, 7)
    assert board.move_robber(3) == []
    assert board.move_robber(0) == []

    board.place_settlement(player1, 5)
    assert board.move_robber(2) == [player1]


@pytest.mark.board
def test_possible_branch_vertices() -> None:
    def setup_board(*roads: int) -> tuple[Board, Player]:
        player1 = Player(1, "red")
        board = Board()
        for road in roads:
            board.place_road(player1, road)
        return board, player1

    board, player1 = setup_board(0, 1, 2, 3, 4, 5, 7)
    assert sorted(board.get_possible_branch_vertices(player1)) == [0, 4, 6, 10]

    board, player1 = setup_board(0, 1, 7, 12, 11, 6)
    assert sorted(board.get_possible_branch_vertices(player1)) == [2, 8, 9, 10]

    board, player1 = setup_board(25, 26, 27, 65, 71)
    assert sorted(board.get_possible_branch_vertices(player1)) == [
        18,
        19,
        20,
        21,
        45,
        52,
    ]

    board, player1 = setup_board(25, 26, 27, 65, 71)
    player2 = Player(2, "blue")
    board.place_settlement(player2, 18)
    board.place_settlement(player2, 45)
    assert sorted(board.get_possible_branch_vertices(player1)) == [
        19,
        20,
        21,
        52,
    ]
