from typing import TYPE_CHECKING
import xml.etree.ElementTree as ET
from enum import Enum
from lib.gameplay.hex import ResourceType
from lib.gameplay.pieces import PieceType
import math
import os
import re
import logging

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from lib.gameplay.game import Game, GameEvent
    from lib.gameplay.hex import Vertex, Edge, Hex


class ResourceColor(Enum):
    BRICK = "red"
    WOOD = "green"
    SHEEP = "white"
    WHEAT = "yellow"
    ORE = "gray"
    DESERT = "beige"


RESOURCE_COLOR_MAP = {
    ResourceType.BRICK: ResourceColor.BRICK.value,
    ResourceType.WOOD: ResourceColor.WOOD.value,
    ResourceType.SHEEP: ResourceColor.SHEEP.value,
    ResourceType.WHEAT: ResourceColor.WHEAT.value,
    ResourceType.ORE: ResourceColor.ORE.value,
    None: ResourceColor.DESERT.value,
}


class Coordinate:
    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y

    def __repr__(self) -> str:
        return f"{self.x}, {self.y}"

    def copy(self) -> "Coordinate":
        return Coordinate(self.x, self.y)

    @staticmethod
    def from_list(input_list: list[float]) -> "Coordinate":
        if len(input_list) < 2:
            raise ValueError("Input list must contain at least 2 elements")
        return Coordinate(input_list[0], input_list[1])


def pair_elements(input_list: list["str"]) -> list[list[str]]:
    # Use list comprehension to create pairs of elements
    return [input_list[i : i + 2] for i in range(0, len(input_list), 2)]


def tangent_line(
    point1: Coordinate, point2: Coordinate, length: float
) -> tuple[Coordinate, Coordinate]:
    """Calculates the coordinates of a tangent line with midpoint at point1 and length l.

    Args:
    - point1: Coordinate, the midpoint of the tangent line.
    - point2: Coordinate, the second point of the initial line.
    - length: The length of the tangent line.

    Returns:
    - A tuple of two Coordinates representing the endpoints of the tangent line.
    """
    x1, y1 = point1.x, point1.y
    x2, y2 = point2.x, point2.y

    # Calculate the slope of the initial line
    if x2 - x1 == 0:  # Vertical line case
        tangent_slope = 0  # Tangent line will be horizontal
    else:
        initial_slope = (y2 - y1) / (x2 - x1)
        tangent_slope = -1 / initial_slope  # Perpendicular slope

    # Angle of the tangent line
    angle = math.atan(tangent_slope)

    # Calculate half of the tangent line length
    half_length = length / 2

    # Endpoint coordinates of the tangent line
    dx = half_length * math.cos(angle)
    dy = half_length * math.sin(angle)

    pointA = Coordinate(x1 - dx, y1 - dy)
    pointB = Coordinate(x1 + dx, y1 + dy)

    return pointA, pointB


class Renderer:
    def __init__(self, game: "Game") -> None:
        self.game = game
        self.game.listen(self.onGameEvent)
        ET.register_namespace("", "http://www.w3.org/2000/svg")
        self.namespace = {"svg": "http://www.w3.org/2000/svg"}

    def onGameEvent(self, event: "GameEvent") -> None:
        self.render()

    def render(self) -> None:
        self.tree = ET.parse("catan_base.svg")

        self.root = self.tree.getroot()
        self.render_hexes()

        # Define the output file path
        output_dir = "public"
        output_file = os.path.join(output_dir, "current.svg")

        # Ensure the output directory exists
        os.makedirs(output_dir, exist_ok=True)

        # Write the SVG to the file
        self.tree.write(output_file, encoding="utf-8", xml_declaration=True)

    def render_hexes(self) -> None:
        hexes = self.game.board.get_hexes()

        for hex in hexes:
            self.set_hex_color(hex.id, RESOURCE_COLOR_MAP[hex.resourceType])
        for hex in hexes:
            self.render_hex_value(hex)
        for vertex in self.game.board.vertices:
            self.render_vertex(vertex)
        self.render_robber(self.game.board.robberLoc)
        for edge in self.game.board.edges:
            self.draw_edge(edge)

    def get_hex_coordinates(self, hexId: int) -> list[Coordinate]:
        hex_element = self.root.find(f".//*[@id='Hex{hexId}']")
        if hex_element is None:
            raise ValueError(f"Element with id='Hex{hexId}' not found")

        polygon = hex_element.find("svg:polygon", self.namespace)
        if polygon is None:
            raise ValueError(f"Polygon not found inside element with id='Hex{hexId}'")

        points = polygon.get("points")
        if points is None:
            raise ValueError("Points attribute not found in polygon")

        return [
            Coordinate.from_list(list(map(float, points)))
            for points in pair_elements(points.strip().split())
        ]

    def draw_edge(self, edge: "Edge") -> None:
        if edge.piece is None:
            return

        hex, edgeLoc = next(iter(edge.hexes.items()))
        coordinateIndex = ((edgeLoc + 4) % 12) // 2
        hexCoordinates = self.get_hex_coordinates(hex.id)[
            coordinateIndex : coordinateIndex + 2
        ]

        self.draw_line(hexCoordinates[0], hexCoordinates[1], edge.piece.player.color)

    def draw_line(self, start: Coordinate, end: Coordinate, color: str) -> None:
        # Create a new line element
        line = ET.Element("line")
        line.set("x1", str(start.x))
        line.set("y1", str(start.y))
        line.set("x2", str(end.x))
        line.set("y2", str(end.y))
        line.set("stroke", color)
        line.set("stroke-width", "8")

        rect = ET.Element("polygon", self.namespace)

        (a, b) = tangent_line(start, end, 8)
        (c, d) = tangent_line(end, start, 8)
        rect.set(
            "points",
            f"{a} {b} {d} {c} {a}",
        )
        rect.set("stroke", "black")
        rect.set("stroke-width", "1")
        rect.set("fill", color)

        # Find the element with id="Hex0"
        hexes_group = self.root.find(".//*[@id='Hexes']")

        if hexes_group is not None:
            hexes_group.append(rect)

    def draw_text(self, x: float, y: float, value: str) -> None:
        # Create a new text element
        text = ET.Element("text")
        text.set("x", str(x - 10))
        text.set("y", str(y + 5))
        text.set("font-size", "24")
        text.set("fill", "black")
        text.text = value

        # Find the element with id="Hexes"
        hexes_group = self.root.find(".//*[@id='Hexes']")

        if hexes_group is not None:
            hexes_group.append(text)

    def get_hex_center(self, hexId: int) -> Coordinate:
        hex_coordinates = self.get_hex_coordinates(hexId)
        minX = min([c.x for c in hex_coordinates])
        maxX = max([c.x for c in hex_coordinates])
        minY = min([c.y for c in hex_coordinates])
        maxY = max([c.y for c in hex_coordinates])
        return Coordinate((minX + maxX) / 2, (minY + maxY) / 2)

    def render_hex_value(self, hex: "Hex") -> None:
        if hex.value is not None:
            center = self.get_hex_center(hex.id)

            self.draw_text(center.x, center.y, str(hex.value))

    def render_vertex(self, vertex: "Vertex") -> None:
        vertex_element = self.root.find(f".//*[@id='Vertex{vertex.id}']")

        if vertex_element is not None:
            polygon = vertex_element.find("svg:polygon", self.namespace)
            if polygon is not None:
                if vertex.piece is not None:
                    color = vertex.piece.player.color
                else:
                    color = "transparent"
                polygon.set("fill", color)

            path = vertex_element.find("svg:path", self.namespace)
            if path is not None:
                if vertex.piece is None:
                    path.set("opacity", "0")
                else:
                    path.set("opacity", "1")
                    if vertex.piece.type == PieceType.CITY:
                        path.set("stroke-width", "5")
                        path.set("stroke", "black")
            else:
                raise ValueError(
                    f"Polygon not found inside element with id='Vertex{vertex.id}'"
                )
        else:
            raise ValueError(f"Element with id='Vertex{vertex.id}' not found")

    def set_hex_color(self, hexId: int, color: str) -> None:
        hex_element = self.root.find(f".//*[@id='Hex{hexId}']")

        if hex_element is not None:
            polygon = hex_element.find("svg:polygon", self.namespace)
            if polygon is not None:
                polygon.set("fill", color)
            else:
                raise ValueError(
                    f"Polygon not found inside element with id='Hex{hexId}'"
                )
        else:
            raise ValueError(f"Element with id='Hex{hexId}' not found")

    def render_robber(self, hexId: int):
        robber_element = self.root.find(".//*[@id='Robber']")
        if robber_element is None:
            raise ValueError("Element with id='Robber' not found")

        paths = robber_element.findall("svg:path", self.namespace)
        center = self.get_hex_center(hexId)

        for path in paths:
            current_d = path.get("d")
            # The current d starts with an M command, so we need to remove it
            current_d = re.sub(
                r"M[\d\.]+,[\d\.]+",
                f"M{round(center.x + 20,2)},{round(center.y + 20,2)}",
                current_d,
            )
            path.set("d", current_d)
            path.set("stroke", "black")
            path.set("stroke-width", "1")
            path.set("fill", "beige")
