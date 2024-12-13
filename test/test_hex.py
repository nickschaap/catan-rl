import pytest
from lib.gameplay.game import Game
from lib.gameplay.hex import Hex, Edge, Vertex, ResourceType
from lib.gameplay.pieces import Settlement, Road
from lib.gameplay.player import Player


@pytest.mark.hex
def test_hex() -> None:
    """Check that each of the properties match"""
    hex = Hex(1)
    assert hex.id == 1
    assert hex.edges == {}
    assert hex.value is None
    assert str(hex) == "Hex 1"
    assert hex == hex

    edge = Edge(1)
    hex.attach_edge(1, edge)

    assert hex.edges[1] == edge
    assert edge.hexes == {hex: 1}

    with pytest.raises(ValueError):
        hex.attach_edge(1, Edge(2))

    with pytest.raises(ValueError):
        hex.attach_edge(2, Edge(1))

    vertex = Vertex(1)

    with pytest.raises(ValueError):
        hex.attach_vertex(1, vertex)

    hex.attach_vertex(2, vertex)

    assert hex.vertices[2] == vertex

    assert vertex.hexes == {hex: 2}

    assert hex.get_settled_players() == []
    assert hex.get_settlements() == []

    hex.attach_value(6)
    assert hex.value == 6

    with pytest.raises(ValueError):
        hex.attach_value(13)

    hex.attach_resource(ResourceType.SHEEP)
    assert hex.resourceType == ResourceType.SHEEP

    with pytest.raises(ValueError):
        hex.attach_resource(ResourceType.SHEEP)

    assert hex.robber is False


@pytest.mark.hex
def test_settlements() -> None:
    game = Game()
    hex = Hex(1)
    vertex = Vertex(1)

    hex.attach_vertex(2, vertex)
    vertex.attach_piece(Settlement(Player(1, "red", game)))

    assert len(hex.get_settlements()) == 1
    settlements = hex.get_settlements()
    assert settlements[0].player.id == 1


@pytest.mark.hex
def test_attach_edges() -> None:
    hex = Hex(1)
    edge = Edge(1)
    edge2 = Edge(2)
    edge3 = Edge(3)
    edge4 = Edge(4)
    edge5 = Edge(5)
    edge6 = Edge(6)

    hex.attach_edges([edge, edge2, edge3, edge4, edge5, edge6])

    assert hex.edges[1] == edge
    assert hex.edges[3] == edge2
    assert hex.edges[5] == edge3
    assert hex.edges[7] == edge4
    assert hex.edges[9] == edge5
    assert hex.edges[11] == edge6

    with pytest.raises(ValueError):
        hex.attach_edges([edge, edge2, edge3, edge4, edge5, edge6, Edge(7)])


@pytest.mark.hex
def test_attach_vertices() -> None:
    hex = Hex(1)
    vertex = Vertex(1)
    vertex2 = Vertex(2)
    vertex3 = Vertex(3)
    vertex4 = Vertex(4)
    vertex5 = Vertex(5)
    vertex6 = Vertex(6)

    hex.attach_vertices([vertex, vertex2, vertex3, vertex4, vertex5, vertex6])

    assert hex.vertices[0] == vertex
    assert hex.vertices[2] == vertex2
    assert hex.vertices[4] == vertex3
    assert hex.vertices[6] == vertex4
    assert hex.vertices[8] == vertex5
    assert hex.vertices[10] == vertex6

    with pytest.raises(ValueError):
        hex.attach_vertices(
            [vertex, vertex2, vertex3, vertex4, vertex5, vertex6, Vertex(7)]
        )


@pytest.mark.hex
def test_vertex() -> None:
    game = Game()
    """Check that each of the properties match"""
    vertex = Vertex(1)
    vertex2 = Vertex(2)
    assert vertex.id == 1
    assert len(vertex.hexes) == 0

    assert vertex == vertex
    assert vertex != vertex2
    assert str(vertex) == "HexPieceType.VERTEX 1"

    hex = Hex(1)
    hex2 = Hex(2)
    hex3 = Hex(3)
    hex4 = Hex(4)

    vertex.attach_hex(hex, 4)
    vertex.attach_hex(hex2, 0)
    vertex.attach_hex(hex3, 2)

    assert len(vertex.hexes) == 3

    assert hex in vertex.hexes
    assert hex2 in vertex.hexes
    assert hex3 in vertex.hexes

    with pytest.raises(ValueError):
        vertex.attach_hex(hex4, 2)

    settlement = Settlement(Player(1, "red", game))
    settlement2 = Settlement(Player(2, "blue", game))

    vertex.attach_piece(settlement)
    assert vertex.piece == settlement

    with pytest.raises(ValueError):
        vertex.attach_piece(settlement2)


@pytest.mark.hex
def test_edge() -> None:
    game = Game()
    edge = Edge(1)

    assert edge.id == 1
    assert str(edge) == "HexPieceType.EDGE 1"

    hex = Hex(1)
    hex2 = Hex(2)
    hex3 = Hex(3)

    edge.attach_hex(hex, 3)
    edge.attach_hex(hex2, 9)

    assert len(edge.hexes) == 2
    assert hex in edge.hexes
    assert hex2 in edge.hexes

    with pytest.raises(ValueError):
        edge.attach_hex(hex3, 3)

    road = Road(Player(1, "red", game))
    road1 = Road(Player(2, "blue", game))
    edge.attach_piece(road)
    assert edge.piece == road

    with pytest.raises(ValueError):
        edge.attach_piece(road1)
