from lib.gameplay.player import Player
from lib.gameplay.hex import ResourceType, Edge
from lib.robot.action_graph import ActionGraph
from typing import TYPE_CHECKING, Union
import logging

logger = logging.getLogger(__name__)

if TYPE_CHECKING:  # pragma: no cover
    from lib.gameplay.board import Board
    from lib.gameplay.bank import Bank
    from lib.gameplay.game import Game


class Robot(Player):
    def __init__(self, id: int, color: str, game: "Game"):
        super().__init__(id, color)
        self.action_graph = ActionGraph(self, game)

    def take_turn(self, board: "Board", bank: "Bank", players: list["Player"]) -> None:
        """Take a turn using a priority-based strategy system."""
        # 1. Calculate current game state and priorities
        my_points = self.points(None, None)  # Current points without bonuses
        resource_counts = self.resource_counts()
        possible_settlements = board.possible_settlement_locations(self)
        possible_roads = board.get_possible_road_locations(self)

        # 2. Priority Actions for Late Game (7+ points)
        if my_points >= 7:
            # Focus on direct point-gaining actions
            if self.can_build_city():
                settlements = self.current_settlements()
                if settlements:
                    position = self._get_best_city_location(settlements, board)
                    logger.info(f"{self} building city at {position}")
                    self.build_city(board, position, bank)
                    return

        # 3. Priority Actions for Mid Game (4-6 points)
        # Try to establish longest road if close
        road_length = board.longest_road(self)
        if road_length >= 3 and self.can_build_road():
            best_road = self._get_best_road_location(possible_roads, board)
            if best_road:
                logger.info(
                    f"{self} building road towards longest road at {best_road.id}"
                )
                self.build_road(board, best_road.id, bank)
                return

        # 4. Priority Actions for Early Game (0-3 points)
        if self.can_build_settlement() and possible_settlements:
            best_spot = self._get_best_settlement_location(possible_settlements, board)
            logger.info(f"{self} building settlement at {best_spot}")
            self.build_settlement(board, best_spot, bank)
            return

        # 5. Resource Management
        self._perform_strategic_trades(resource_counts, bank)

        # 6. Fallback Actions
        if self.can_build_road() and possible_roads:
            best_road = self._get_best_road_location(possible_roads, board)
            if best_road:
                logger.info(f"{self} building road at {best_road.id}")
                self.build_road(board, best_road.id, bank)

    def _get_best_settlement_location(
        self, possible_locations: list[int], board: "Board"
    ) -> int:
        """Choose best settlement location based on resource diversity and probability."""
        location_scores = {}
        for loc in possible_locations:
            vertex = board.vertices[loc]
            score = 0
            resources_seen = set()

            for hex in vertex.hexes:
                if hex.resourceType is not None:
                    score += hex.likelihood() * 2  # Weight by probability
                    if hex.resourceType not in resources_seen:
                        score += 1  # Bonus for resource diversity
                        resources_seen.add(hex.resourceType)

            location_scores[loc] = score

        return max(location_scores.items(), key=lambda x: x[1])[0]

    def _get_best_road_location(
        self, possible_locations: list["Edge"], board: "Board"
    ) -> Union["Edge", None]:
        """Choose best road location prioritizing longest road potential."""
        if not possible_locations:
            return None

        road_scores = {}
        for edge in possible_locations:
            score = 0
            # Prefer roads that connect to existing settlements
            for vertex in edge.vertices():
                if vertex.piece and vertex.piece.player == self:
                    score += 3
                # Prefer roads that could lead to new settlement locations
                elif board.can_settle(vertex.id):
                    score += 2
            # Prefer roads that connect to existing roads
            for connected_edge in edge.connected_edges(self):
                if connected_edge.piece and connected_edge.piece.player == self:
                    score += 1

            road_scores[edge] = score

        return max(road_scores.items(), key=lambda x: x[1])[0]

    def _perform_strategic_trades(
        self, resource_counts: dict[ResourceType, int], bank: "Bank"
    ) -> None:
        """Perform strategic trades based on current needs and game state."""
        needed_resources = self._calculate_needed_resources()

        for resource, count in resource_counts.items():
            if count >= 4:
                # Don't trade away ore if we're close to a city
                if resource == ResourceType.ORE and self.can_build_city():
                    continue

                # Find most needed resource
                for needed in needed_resources:
                    if resource_counts[needed] < 2:  # Only trade if we're low
                        logger.info(f"{self} trading 4 {resource} for 1 {needed}")
                        self.trade_bank([resource] * 4, needed, bank)
                        break

    def _calculate_needed_resources(self) -> list[ResourceType]:
        """Calculate which resources are most needed based on current strategy."""
        if self.can_build_city():
            return [ResourceType.ORE, ResourceType.WHEAT]
        elif self.can_build_settlement():
            return [
                ResourceType.BRICK,
                ResourceType.WOOD,
                ResourceType.SHEEP,
                ResourceType.WHEAT,
            ]
        else:
            return [ResourceType.BRICK, ResourceType.WOOD]  # Default to road resources
