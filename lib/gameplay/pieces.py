from __future__ import annotations
from lib.gameplay.hex import ResourceType
from typing import Union
from enum import Enum
from lib.gameplay.hex import Vertex

from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from lib.gameplay.player import Player
    from lib.gameplay.board import Board


class PieceType(Enum):
    SETTLEMENT = 1
    ROAD = 2
    CITY = 3


class Piece:
    count = 0

    def __init__(
        self,
        type: PieceType,
        player: Player,
        position: Union[int, None] = None,
    ):
        self.type = type
        self.player = player
        self.position = position
        Piece.count += 1
        self.id = self.count

    def __repr__(self):
        return f"{self.type} {self.id}"

    def set_position(self, position: int) -> None:
        self.position = position


class Settlement(Piece):
    vertex: Union[Vertex, None] = None

    def __init__(self, player: Player, position: Union[int, None] = None):
        super().__init__(PieceType.SETTLEMENT, player, position)

    def set_vertex(self, vertex: Union[Vertex, None]) -> None:
        if vertex is not None:
            self.position = vertex.id
        else:
            self.position = None
        self.vertex = vertex

    def get_resources(self) -> list[ResourceType]:
        hexes = self.vertex.hexes
        return [hex.resourceType for hex in hexes if hex.resourceType is not None]

    def get_points(self) -> int:
        if self.position is None:
            return 0
        return 1


class City(Piece):
    vertex: Union[Vertex, None] = None

    def __init__(self, player: Player, position: Union[int, None] = None):
        super().__init__(PieceType.CITY, player, position)

    def set_vertex(self, vertex: Union[Vertex, None]) -> None:
        if vertex is not None:
            self.position = vertex.id
        else:
            self.position = None
        self.vertex = vertex

    def get_points(self) -> int:
        if self.position is None:
            return 0
        return 2


class Road(Piece):
    def __init__(self, player: Player, position: Union[int, None] = None):
        super().__init__(PieceType.ROAD, player, position)

    def get_connecting_roads(self, board: "Board") -> list[Road]:
        if self.position is None:
            return []
        edge = board.edges[self.position]
        return [
            e.piece
            for e in edge.north_neighbor().connected_edges()
            if e.piece is not None
            and e.piece.player == self.player
            and e != edge
            and isinstance(e.piece, Road)
        ] + [
            e.piece
            for e in edge.south_neighbor().connected_edges()
            if e.piece is not None
            and e.piece.player == self.player
            and e != edge
            and isinstance(e.piece, Road)
        ]

    def get_num_branches(self, board: "Board") -> int:
        return len(self.get_connecting_roads(board))


class CardType(Enum):
    KNIGHT = 1
    VICTORY_POINT = 2
    MONOPOLY = 3
    YEAR_OF_PLENTY = 4
    ROAD_BUILDING = 5


class DevelopmentCard:
    def __init__(self, cardType: CardType):
        self.cardType = cardType

    def get_type(self) -> CardType:
        return self.cardType

    def get_points(self) -> int:
        if self.cardType == CardType.VICTORY_POINT:
            return 1
        return 0


class ResourceCard:
    def __init__(self, resourceType: ResourceType):
        self.resourceType = resourceType

    def get_type(self) -> ResourceType:
        return self.resourceType

    def __deepcopy__(self, _memo: dict[int, ResourceCard]) -> ResourceCard:
        return ResourceCard(self.resourceType)
