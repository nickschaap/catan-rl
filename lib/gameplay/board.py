from lib.gameplay.hex import Hex, ResourceType, Edge, Vertex
from lib.gameplay.pieces import Road, PieceType
from collections import deque

from typing import TYPE_CHECKING, Set, Union

if TYPE_CHECKING:  # pragma: no cover
    from lib.gameplay.player import Player


class Board:
    def __init__(self):
        self.setup_hexes()
        self.robberLoc = 9

    def setup_hexes(self):
        self.hexes = [Hex(i) for i in range(19)]
        self.edges = [Edge(i) for i in range(72)]
        self.vertices = [Vertex(i) for i in range(54)]

        def get_vertices(*indices: int) -> list[Vertex]:
            return [self.vertices[i] for i in indices]

        def get_edges(*indices: int) -> list[Edge]:
            return [self.edges[i] for i in indices]

        self.hexes[0].attach_resource(ResourceType.ORE)
        self.hexes[0].attach_value(10)
        self.hexes[0].attach_edges(get_edges(1, 7, 12, 11, 6, 0))
        self.hexes[0].attach_vertices(get_vertices(1, 2, 10, 9, 8, 0))
        self.hexes[1].attach_resource(ResourceType.SHEEP)
        self.hexes[1].attach_value(2)
        self.hexes[1].attach_edges(get_edges(3, 8, 14, 13, 7, 2))
        self.hexes[1].attach_vertices(get_vertices(3, 4, 12, 11, 10, 2))
        self.hexes[2].attach_resource(ResourceType.WOOD)
        self.hexes[2].attach_value(9)
        self.hexes[2].attach_edges(get_edges(5, 9, 16, 15, 8, 4))
        self.hexes[2].attach_vertices(get_vertices(5, 6, 14, 13, 12, 4))
        self.hexes[3].attach_resource(ResourceType.WHEAT)
        self.hexes[3].attach_value(12)
        self.hexes[3].attach_edges(get_edges(11, 19, 25, 24, 18, 10))
        self.hexes[3].attach_vertices(get_vertices(8, 9, 19, 18, 17, 7))
        self.hexes[4].attach_resource(ResourceType.BRICK)
        self.hexes[4].attach_value(6)
        self.hexes[4].attach_edges(get_edges(13, 20, 27, 26, 19, 12))
        self.hexes[4].attach_vertices(get_vertices(10, 11, 21, 20, 19, 9))
        self.hexes[5].attach_resource(ResourceType.SHEEP)
        self.hexes[5].attach_value(4)
        self.hexes[5].attach_edges(get_edges(15, 21, 29, 28, 20, 14))
        self.hexes[5].attach_vertices(get_vertices(12, 13, 23, 22, 21, 11))
        self.hexes[6].attach_resource(ResourceType.BRICK)
        self.hexes[6].attach_value(10)
        self.hexes[6].attach_edges(get_edges(17, 22, 31, 30, 21, 16))
        self.hexes[6].attach_vertices(get_vertices(14, 15, 25, 24, 23, 13))
        self.hexes[7].attach_resource(ResourceType.WHEAT)
        self.hexes[7].attach_value(9)
        self.hexes[7].attach_edges(get_edges(24, 34, 40, 39, 33, 23))
        self.hexes[7].attach_vertices(get_vertices(17, 18, 29, 28, 27, 16))
        self.hexes[8].attach_resource(ResourceType.WOOD)
        self.hexes[8].attach_value(11)
        self.hexes[8].attach_edges(get_edges(26, 35, 42, 41, 34, 25))
        self.hexes[8].attach_vertices(get_vertices(19, 20, 31, 30, 29, 18))
        # self.hexes[9] is the desert
        self.hexes[9].robber = True
        self.hexes[9].attach_edges(get_edges(28, 36, 44, 43, 35, 27))
        self.hexes[9].attach_vertices(get_vertices(21, 22, 33, 32, 31, 20))
        self.hexes[10].attach_resource(ResourceType.WOOD)
        self.hexes[10].attach_value(3)
        self.hexes[10].attach_edges(get_edges(30, 37, 46, 45, 36, 29))
        self.hexes[10].attach_vertices(get_vertices(23, 24, 35, 34, 33, 22))
        self.hexes[11].attach_resource(ResourceType.ORE)
        self.hexes[11].attach_value(8)
        self.hexes[11].attach_edges(get_edges(32, 38, 48, 47, 37, 31))
        self.hexes[11].attach_vertices(get_vertices(25, 26, 37, 36, 35, 24))
        self.hexes[12].attach_resource(ResourceType.WOOD)
        self.hexes[12].attach_value(8)
        self.hexes[12].attach_edges(get_edges(41, 50, 55, 54, 49, 40))
        self.hexes[12].attach_vertices(get_vertices(29, 30, 40, 39, 38, 28))
        self.hexes[13].attach_resource(ResourceType.ORE)
        self.hexes[13].attach_value(3)
        self.hexes[13].attach_edges(get_edges(43, 51, 57, 56, 50, 42))
        self.hexes[13].attach_vertices(get_vertices(31, 32, 42, 41, 40, 30))
        self.hexes[14].attach_resource(ResourceType.WHEAT)
        self.hexes[14].attach_value(4)
        self.hexes[14].attach_edges(get_edges(45, 52, 59, 58, 51, 44))
        self.hexes[14].attach_vertices(get_vertices(33, 34, 44, 43, 42, 32))
        self.hexes[15].attach_resource(ResourceType.SHEEP)
        self.hexes[15].attach_value(5)
        self.hexes[15].attach_edges(get_edges(47, 53, 61, 60, 52, 46))
        self.hexes[15].attach_vertices(get_vertices(35, 36, 46, 45, 44, 34))
        self.hexes[16].attach_resource(ResourceType.BRICK)
        self.hexes[16].attach_value(5)
        self.hexes[16].attach_edges(get_edges(56, 63, 67, 66, 62, 55))
        self.hexes[16].attach_vertices(get_vertices(40, 41, 49, 48, 47, 39))
        self.hexes[17].attach_resource(ResourceType.WHEAT)
        self.hexes[17].attach_value(6)
        self.hexes[17].attach_edges(get_edges(58, 64, 69, 68, 63, 57))
        self.hexes[17].attach_vertices(get_vertices(42, 43, 51, 50, 49, 41))
        self.hexes[18].attach_resource(ResourceType.SHEEP)
        self.hexes[18].attach_value(11)
        self.hexes[18].attach_edges(get_edges(60, 65, 71, 70, 64, 59))
        self.hexes[18].attach_vertices(get_vertices(44, 45, 53, 52, 51, 43))

    def place_settlement(self, player: "Player", vertexLoc: int) -> None:
        """Place a settlement at a vertex location"""
        if not self.can_settle(vertexLoc):
            raise ValueError("Invalid settlement location")
        vertex = self.vertices[vertexLoc]
        settlement = player.get_unplaced_settlement()
        if settlement is None:
            raise ValueError("No unplaced settlements available")
        vertex.attach_piece(settlement)
        settlement.set_vertex(vertex)

    def place_city(self, player: "Player", vertexLoc: int) -> None:
        """Upgrade a settlement to a city"""
        vertex = self.vertices[vertexLoc]
        if vertex.piece is None:
            raise ValueError("No settlement at vertex")
        if vertex.piece.player != player:
            raise ValueError("Settlement belongs to another player")
        if vertex.piece.type == PieceType.CITY:
            raise ValueError("City already placed at location")
        city = player.get_unplaced_city()
        if city is None:
            raise ValueError("No unplaced cities available")
        settlement = vertex.piece
        vertex.piece = None
        settlement.position = None
        vertex.attach_piece(city)
        city.set_vertex(vertex)

    def place_road(self, player: "Player", edgeLoc: int) -> None:
        """Place a road at an edge location"""
        edge = self.edges[edgeLoc]
        if edge.piece is not None:
            raise ValueError("Edge is already occupied")
        road = player.get_unplaced_road()
        if road is None:
            raise ValueError("No unplaced roads available")
        edge.attach_piece(road)
        road.set_position(edgeLoc)

    def get_settlements(self) -> list[Vertex]:
        return [vertex for vertex in self.vertices if vertex.piece is not None]

    def get_roads(self) -> list[Edge]:
        return [edge for edge in self.edges if edge.piece is not None]

    def get_hexes(self) -> list[Hex]:
        return self.hexes

    def shortest_path(self, player: "Player", vertexLoc: int) -> list[Edge]:
        """Find shortest path of unoccupied edges from player's branch vertices to target vertex

        Args:
            player: Player to find path for
            vertexLoc: Target vertex location to path to

        Returns:
            List of unoccupied edges forming shortest path, or empty list if no path exists
        """
        # TODO: There could be mulitple shortest paths, we should return all of them
        target_vertex = self.vertices[vertexLoc]
        branch_vertices = [
            self.vertices[v] for v in self.get_possible_branch_vertices(player)
        ]

        # Track visited vertices and previous edges in path
        visited = set()
        prev_edge = {}

        # BFS queue contains (vertex, edge that led to it)
        queue = deque()

        # Add all starting vertices
        for vertex in branch_vertices:
            visited.add(vertex)
            queue.append((vertex, None))

        # BFS to find shortest path
        while queue:
            current_vertex, prev = queue.popleft()

            if current_vertex == target_vertex:
                # Found target, reconstruct path
                path = []
                current = current_vertex
                while current in prev_edge:
                    path.append(prev_edge[current])
                    # Get vertex at other end of edge
                    current = (
                        prev_edge[current].north_neighbor()
                        if prev_edge[current].south_neighbor() == current
                        else prev_edge[current].south_neighbor()
                    )
                return list(reversed(path))

            # Check all unoccupied connected edges
            for edge in current_vertex.connected_edges():
                if edge.piece is not None:
                    continue

                # Get vertex at other end of edge
                next_vertex = (
                    edge.north_neighbor()
                    if edge.south_neighbor() == current_vertex
                    else edge.south_neighbor()
                )

                # Skip if vertex has another player's piece
                if next_vertex.piece is not None and next_vertex.piece.player != player:
                    continue

                if next_vertex not in visited:
                    visited.add(next_vertex)
                    prev_edge[next_vertex] = edge
                    queue.append((next_vertex, edge))

        return []  # No path found

    def longest_road(self, player: "Player") -> int:
        player_roads = [road for road in player.roads if road.position is not None]
        player_roads.sort(key=lambda road: road.get_num_branches(self), reverse=True)
        visited_roads = set()

        def get_edge(road: Union["Road", None]) -> Edge:
            if road is None:  # pragma: no cover
                raise ValueError("Road is None")
            edgeLoc = road.position
            if edgeLoc is None:  # pragma: no cover
                raise ValueError("Edge location is None")
            return self.edges[edgeLoc]

        def get_branch_roads(vertex: "Vertex", visited: Set["Road"]) -> list["Road"]:
            if vertex.piece is not None and vertex.piece.player != player:
                return []
            return [
                edge.piece
                for edge in vertex.connected_edges()
                if edge.piece is not None
                and edge.piece.player == player
                and isinstance(edge.piece, Road)
                and edge.piece not in visited
            ]

        def get_longest_starting_from(
            road: "Road",
            visited: Set["Road"],
            longest_so_far: int,
            exclude_initial: Set["Road"] = set(),
        ) -> int:
            if road in visited:
                return 0

            visited_roads.add(road)
            edge = get_edge(road)
            north_branch_roads = get_branch_roads(
                edge.north_neighbor(), visited | exclude_initial
            )
            south_branch_roads = get_branch_roads(
                edge.south_neighbor(), visited | exclude_initial
            )

            if len(north_branch_roads) == 0 and len(south_branch_roads) == 0:
                return longest_so_far + 1
            if len(north_branch_roads) == 1 and len(south_branch_roads) == 1:
                north_longest_road = get_longest_starting_from(
                    north_branch_roads[0], visited, 0
                )
                south_longest_road = get_longest_starting_from(
                    south_branch_roads[0], visited, 0
                )
                return north_longest_road + south_longest_road + 1
            elif len(north_branch_roads) == 1 and len(south_branch_roads) == 0:
                return get_longest_starting_from(
                    north_branch_roads[0], visited, longest_so_far + 1
                )
            elif len(north_branch_roads) == 0 and len(south_branch_roads) == 1:
                return get_longest_starting_from(
                    south_branch_roads[0], visited, longest_so_far + 1
                )

            lengths = []
            north_branch_roads = get_branch_roads(
                edge.north_neighbor(), visited | exclude_initial
            )
            north_branch_road_lengths = [0]
            while len(north_branch_roads) > 0:
                north_branch_road_lengths.append(
                    get_longest_starting_from(
                        north_branch_roads[0],
                        visited,
                        0,
                        set(north_branch_roads[1:]),
                    )
                )
                north_branch_roads = get_branch_roads(edge.north_neighbor(), visited)

            south_branch_roads = get_branch_roads(
                edge.south_neighbor(), visited | exclude_initial
            )
            south_branch_road_lengths = [0]
            while len(south_branch_roads) > 0:
                south_branch_road_lengths.append(
                    get_longest_starting_from(
                        south_branch_roads[0], visited, 0, set(south_branch_roads[1:])
                    )
                )
                south_branch_roads = get_branch_roads(
                    edge.south_neighbor(), visited | exclude_initial
                )

            lengths.append(
                max(north_branch_road_lengths)
                + max(south_branch_road_lengths)
                + longest_so_far
                + 1
            )

            if len(north_branch_road_lengths) == 3:
                lengths.append(
                    north_branch_road_lengths[1] + north_branch_road_lengths[2]
                )
            if len(south_branch_road_lengths) == 3:
                lengths.append(
                    south_branch_road_lengths[1] + south_branch_road_lengths[2]
                )

            return max(lengths)

        longest = 0
        for road in player_roads:
            if road not in visited_roads:
                length = get_longest_starting_from(road, visited_roads, 0)
                longest = max(longest, length)
        return longest

    def can_player_settle(self, player: "Player", vertexLoc: int) -> bool:
        """Check if a player can settle at a vertex location"""
        vertex = self.vertices[vertexLoc]
        if vertex.piece is not None:
            return False

        def has_roads(vertex: "Vertex") -> bool:
            return any(
                edge.piece is not None and edge.piece.player == player
                for edge in vertex.connected_edges()
            )

        return self.can_settle(vertexLoc) and has_roads(vertex)

    def can_settle(self, vertexLoc: int) -> bool:
        """Check if a vertex location is within the range of a settlement"""
        vertex = self.vertices[vertexLoc]
        if vertex.piece is not None:
            return False

        for edge in vertex.connected_edges():
            for neighborVertex in edge.vertices():
                if neighborVertex != vertex and neighborVertex.piece is not None:
                    return False
        return True

    def get_edge(self, road: "Road") -> Edge:
        edgeLoc = road.position
        if edgeLoc is None:
            raise ValueError("Edge location is None")
        return self.edges[edgeLoc]

    def get_possible_branch_vertices(self, player: "Player") -> list[int]:
        """Return a list of possible branch vertices for a player"""
        player_roads = [road for road in player.roads if road.position is not None]

        vertices = set()
        for road in player_roads:
            edge = self.get_edge(road)
            vertices = vertices.union(edge.vertices())
        return [
            v.id
            for v in vertices
            if (v.piece is None or v.piece.player == player)
            and any([v.piece is None for v in v.connected_edges()])
        ]

    def get_possible_road_locations(self, player: "Player") -> list[Edge]:
        """Return a list of possible road locations for a player"""
        vertices = [self.vertices[v] for v in self.get_possible_branch_vertices(player)]
        edges: Set[Edge] = set()
        for vertex in vertices:
            for edge in vertex.connected_edges():
                if edge.piece is None:
                    edges.add(edge)
        return list(edges)

    def possible_settlement_locations(self, player: "Player") -> list[int]:
        """Return a list of possible settlement locations for a player"""
        player_roads = [road for road in player.roads if road.position is not None]

        def get_edge(road: "Road") -> Edge:
            edgeLoc = road.position
            if edgeLoc is None:
                raise ValueError("Edge location is None")
            return self.edges[edgeLoc]

        vertices = set()
        for road in player_roads:
            edge = get_edge(road)
            vertices = vertices.union(edge.vertices())

        return [v.id for v in vertices if self.can_settle(v.id)]

    def move_robber(self, hexLoc: int) -> list["Player"]:
        """Move the robber to a new hex location and return a list of players who have pieces on that hex"""
        self.hexes[self.robberLoc].robber = False
        self.robberLoc = hexLoc
        self.hexes[hexLoc].robber = True

        pieces = [
            v.piece for v in self.hexes[hexLoc].vertices.values() if v.piece is not None
        ]
        return list(set([p.player for p in pieces]))
