from __future__ import annotations
from enum import Enum
from typing import TYPE_CHECKING
from typing import Union, Set

if TYPE_CHECKING:  # pragma: no cover
    from lib.gameplay.pieces import Piece
    from lib.gameplay.player import Player


class ResourceType(Enum):
    WOOD = 1
    BRICK = 2
    SHEEP = 3
    WHEAT = 4
    ORE = 5


class HexPieceType(Enum):
    VERTEX = 1
    EDGE = 2


class HexPiece:
    def __init__(self, id: int, type: HexPieceType):
        self.id = id
        self.type = type
        self.hexes: dict["Hex", int] = dict()
        self.piece: Union[Piece, None] = None
        self.max_hexes = 3 if type == HexPieceType.VERTEX else 2

    def __eq__(self, value: "HexPiece") -> bool:
        return isinstance(value, HexPiece) and self.id == value.id

    def __repr__(self):
        return f"{self.type} {self.id}"

    def __hash__(self):
        return self.id

    def attach_hex(self, hex: "Hex", loc: int):
        if hex not in self.hexes:
            self.hexes[hex] = loc
        if len(self.hexes) > self.max_hexes:
            raise ValueError("Too many hexes")

    def attach_piece(self, piece: Piece):
        if self.piece is not None:
            raise ValueError("Piece already attached")
        self.piece = piece


class Vertex(HexPiece):
    def __init__(self, id: int):
        super().__init__(id, HexPieceType.VERTEX)

    def connected_edges(self) -> list[Edge]:
        edges: Set[Edge] = set()
        for index, (hex, loc) in enumerate(self.hexes.items()):
            edges.add(hex.edges[(loc + 1) % 12])
            edges.add(hex.edges[(loc + 11) % 12])
            if index == 1:
                break
        return list(edges)


class Edge(HexPiece):
    def __init__(self, id: int):
        super().__init__(id, HexPieceType.EDGE)

    def north_neighbor(self) -> Vertex:
        hex, hexLoc = next(iter(self.hexes.items()))
        if hexLoc < 6:
            return hex.vertices[hexLoc - 1]
        else:
            return hex.vertices[(hexLoc + 1) % 12]

    def south_neighbor(self) -> Vertex:
        hex, hexLoc = next(iter(self.hexes.items()))
        if hexLoc < 6:
            return hex.vertices[hexLoc + 1]
        else:
            return hex.vertices[hexLoc - 1]

    def vertices(self) -> list[Vertex]:
        return [self.north_neighbor(), self.south_neighbor()]


VERTEX_LOCATIONS = [0, 2, 4, 6, 8, 10]
EDGE_LOCATIONS = [1, 3, 5, 7, 9, 11]


class Hex:
    def __init__(self, id: int):
        self.edges: dict[int, Edge] = {}
        self.vertices: dict[int, Vertex] = {}
        self.id = id
        self.resourceType = None
        self.value = None
        self.robber = False

    def __hash__(self):
        return self.id

    def __repr__(self):
        return f"Hex {self.id}"

    def __eq__(self, value: "Hex") -> bool:
        return isinstance(value, Hex) and self.id == value.id

    def attach_resource(self, resourceType: ResourceType):
        if self.resourceType is not None:
            raise ValueError("Resource already attached")
        self.resourceType = resourceType

    def attach_value(self, value: int):
        if value < 2 or value > 12:
            raise ValueError("Invalid value")
        self.value = value

    def attach_edges(self, edges: list[Edge]):
        if len(edges) != 6:
            raise ValueError("Must have 6 edges")
        for i, edge in enumerate(edges):
            self.attach_edge(EDGE_LOCATIONS[i], edge)

    def attach_edge(self, location: int, edge: Edge):
        if location % 2 == 1 and location not in self.edges:
            self.edges[location] = edge
            edge.attach_hex(self, location)
        else:
            raise ValueError("Location must be odd")

    def attach_vertices(self, vertices: list[Vertex]):
        if len(vertices) != 6:
            raise ValueError("Must have 6 vertices")
        for i, vertex in enumerate(vertices):
            self.attach_vertex(VERTEX_LOCATIONS[i], vertex)

    def attach_vertex(self, location: int, vertex: Vertex):
        if location % 2 == 0 and location not in self.vertices:
            self.vertices[location] = vertex
            vertex.attach_hex(self, location)
        else:
            raise ValueError("Location must be even")

    def get_settlements(self) -> list[Piece]:
        return [
            vertex.piece
            for vertex in self.vertices.values()
            if vertex.piece is not None
        ]

    def get_settled_players(self) -> list[Player]:
        return [piece.player for piece in self.get_settlements()]
