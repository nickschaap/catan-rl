from typing import TYPE_CHECKING

from enum import Enum
from lib.gameplay.hex import Vertex, Edge, ResourceType


class ActionType(Enum):
    BUILD_ROAD = 1
    BUILD_SETTLEMENT = 2
    BUILD_CITY = 3
    BUY_DEVELOPMENT_CARD = 4


if TYPE_CHECKING:
    from lib.gameplay.player import Player
    from lib.gameplay.board import Board
    from lib.gameplay.bank import Bank
    from lib.gameplay.game import Game


class Action:
    def __init__(self, action_type: ActionType, graph: "ActionGraph"):
        self.action_type = action_type
        self.graph = graph
        self.game = graph.game
        self.player = graph.player
        self.board = graph.game.board

    def depends_on(self) -> list["Action"]:
        # A dynamic list of actions that should be taken which minimize the cost of the action
        return []

    def cost(self) -> int:
        """The direct cost of the action"""
        return 0

    def reward(self) -> int:
        """The reward of the action"""
        return 0

    def can_execute(self, board: "Board", bank: "Bank", player: "Player") -> bool:
        return True

    def execute(
        self, board: "Board", bank: "Bank", player: "Player", players: list["Player"]
    ) -> None:
        pass

    def __str__(self) -> str:
        return f"{self.action_type}"


class BuildRoad(Action):
    def __init__(self, edge: Edge, graph: "ActionGraph"):
        super().__init__(ActionType.BUILD_ROAD, graph)
        self.edge = edge

    def can_execute(self, board: "Board", bank: "Bank", player: "Player") -> bool:
        return super().can_execute(board, bank, player)

    def __str__(self) -> str:
        return f"{self.action_type} {self.edge.id}"


class BuildSettlement(Action):
    def __init__(self, vertex: Vertex, graph: "ActionGraph"):
        super().__init__(ActionType.BUILD_SETTLEMENT, graph)
        self.vertex = vertex

    def min_distance_to_road(self) -> str:
        return ", ".join(
            [
                str(edge)
                for edge in self.board.shortest_path(self.player, self.vertex.id)
            ]
        )

    def resources_at_hex(self) -> str:
        return ", ".join(
            [
                f"{hex.resourceType} ({hex.value})"
                for hex in self.vertex.get_hexes()
                if hex.resourceType is not None
            ]
        )

    def __str__(self) -> str:
        return f"{self.action_type} {self.vertex.id} <ul><li>Min Distance to Road: {self.min_distance_to_road()}</li><li>Resources at Hex: {self.resources_at_hex()}</li></ul>"


class BuildCity(Action):
    def __init__(self, vertex: Vertex, graph: "ActionGraph"):
        super().__init__(ActionType.BUILD_CITY, graph)
        self.vertex = vertex

    def resources_at_hex(self) -> str:
        return ", ".join(
            [
                f"{hex.resourceType} ({hex.value})"
                for hex in self.vertex.get_hexes()
                if hex.resourceType is not None
            ]
        )

    def __str__(self) -> str:
        return f"{self.action_type} {self.vertex.id}  <ul><li>Resources at Hex: {self.resources_at_hex()}</li></ul>"


class ActionGraph:
    def __init__(self, player: "Player", game: "Game"):
        self.player = player
        self.game = game

    def get_actions(self) -> list[Action]:
        board = self.game.board
        settlement_actions = [
            BuildSettlement(vertex, self)
            for vertex in board.vertices
            if vertex.piece is None and board.can_settle(vertex.id)
        ]

        road_actions = [
            BuildRoad(edge, self) for edge in board.edges if edge.piece is None
        ]

        city_actions = [
            BuildCity(settlement.vertex, self)
            for settlement in self.player.get_active_settlements()
        ]

        return settlement_actions + road_actions + city_actions


"""
Building an action graph.

Let's say we start with an action BuildSettlement(vertexLoc: int)


Is it possible (given enough resources) to build a settlement on the vertex?
We can see if this is possible by checking if the vertexLoc is a valid vertex on the board.
We can see if this possible by checking that no other player has a settlement on the vertex.
We can see if this is possible by checking to see if the player can build a road from their pre-established roads to arrive at the vertex.

How can we calculate the cost of the action?
How many roads need to be built to connect the vertex to the player's roads?
Is the player well positioned to be building roads given their current resources probabilities?

Let's say we start with an action 

"""
