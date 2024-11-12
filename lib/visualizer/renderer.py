from typing import TYPE_CHECKING
import xml.etree.ElementTree as ET
from enum import Enum
from lib.gameplay.hex import ResourceType
import math

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

    def __repr__(self):
        return f"{self.x}, {self.y}"

    def copy(self) -> "Coordinate":
        return Coordinate(self.x, self.y)

    @staticmethod
    def from_list(input_list: list[float]) -> "Coordinate":
        return Coordinate(input_list[0], input_list[1])


def pair_elements(input_list: list["str"]) -> list[list[str]]:
    # Use list comprehension to create pairs of elements
    return [input_list[i : i + 2] for i in range(0, len(input_list), 2)]


def tangent_line(
    point1: Coordinate, point2: Coordinate, length: float
) -> tuple[Coordinate, Coordinate]:
    """
    Calculates the coordinates of a tangent line with midpoint at point1 and length l.

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

    def onGameEvent(self, event: "GameEvent") -> None:
        self.render()

    def render(self) -> None:
        self.tree = ET.parse("catan_base.svg")
        ET.register_namespace("", "http://www.w3.org/2000/svg")
        self.root = self.tree.getroot()
        self.render_hexes()
        self.tree.write("current.svg")

    def render_hexes(self) -> None:
        hexes = self.game.board.get_hexes()

        for hex in hexes:
            self.set_hex_color(hex.id, RESOURCE_COLOR_MAP[hex.resourceType])
        for hex in hexes:
            self.render_hex_value(hex)
        for vertex in self.game.board.vertices:
            self.render_vertex(vertex)
        for edge in self.game.board.edges:
            self.draw_edge(edge)

    def get_hex_coordinates(self, hexId: int) -> list[Coordinate]:
        # Define the SVG namespace
        namespace = {"svg": "http://www.w3.org/2000/svg"}

        # Find the element with id="Hex0"
        hex_element = self.root.find(f".//*[@id='Hex{hexId}']", namespace)

        if hex_element is not None:
            # Find the polygon inside the hex group
            polygon = hex_element.find("svg:polygon", namespace)
            if polygon is not None:
                # Change the fill attribute
                points = polygon.get("points")
                if points is not None:
                    # l: list[Coordinate] = list(
                    #     reversed(
                    #         [
                    #             Coordinate.from_list(list(map(float, points)))
                    #             for points in pair_elements(points.strip().split())
                    #         ]
                    #     )
                    # )
                    l = [
                        Coordinate.from_list(list(map(float, points)))
                        for points in pair_elements(points.strip().split())
                    ]

                    # l.append(l[0].copy())
                    # l.pop(0)
                    # l.append(l[0].copy())
                    # l.pop(0)
                    # l.append(l[0].copy())
                    # l.pop(0)
                    # l.append(l[0].copy())
                    # l.pop(0)

                    return l
                raise ValueError("Points attribute not found in polygon")
            else:
                raise ValueError("Polygon not found inside element with id='Hex0'")
        else:
            raise ValueError(f"Element with id='Hex{hexId}' not found")

    def draw_edge(self, edge: "Edge") -> None:
        if edge.piece is None:
            return

        hex, edgeLoc = next(iter(edge.hexes.items()))

        coordinateIndex = ((edgeLoc + 4) % 12) // 2

        hexCoordinates = self.get_hex_coordinates(hex.id)[
            coordinateIndex : coordinateIndex + 2
        ]

        start = hexCoordinates[0]
        end = hexCoordinates[1]

        self.draw_line(start, end, edge.piece.player.color)

    def draw_line(self, start: Coordinate, end: Coordinate, color: str) -> None:
        # Create a new line element
        line = ET.Element("line")
        line.set("x1", str(start.x))
        line.set("y1", str(start.y))
        line.set("x2", str(end.x))
        line.set("y2", str(end.y))
        line.set("stroke", color)
        line.set("stroke-width", "8")

        rect = ET.Element("polygon")

        (a, b) = tangent_line(start, end, 8)
        (c, d) = tangent_line(end, start, 8)
        rect.set(
            "points",
            f"{a} {b} {d} {c} {a}",
        )
        rect.set("stroke", "black")
        rect.set("stroke-width", "1")
        rect.set("fill", color)

        namespace = {"svg": "http://www.w3.org/2000/svg"}
        # Find the element with id="Hex0"
        hexes_group = self.root.find(f".//*[@id='Hexes']", namespace)

        if hexes_group is not None:
            # hexes_group.append(line)
            hexes_group.append(rect)

    def draw_text(self, x: float, y: float, value: str) -> None:
        # Create a new text element
        text = ET.Element("text")
        text.set("x", str(x))
        text.set("y", str(y))
        text.set("font-size", "24")
        text.set("fill", "black")
        text.text = value

        namespace = {"svg": "http://www.w3.org/2000/svg"}

        hexes_group = self.root.find(f".//*[@id='Hexes']", namespace)

        if hexes_group is not None:
            hexes_group.append(text)

    def render_hex_value(self, hex: "Hex") -> None:
        if hex.value is not None:
            hexCoordinates = self.get_hex_coordinates(hex.id)
            minX = min([c.x for c in hexCoordinates])
            maxX = max([c.x for c in hexCoordinates])
            minY = min([c.y for c in hexCoordinates])
            maxY = max([c.y for c in hexCoordinates])

            center = Coordinate((minX + maxX) / 2, (minY + maxY) / 2)
            self.draw_text(center.x, center.y, str(hex.value))

    def render_vertex(self, vertex: "Vertex") -> None:
        # Define the SVG namespace
        namespace = {"svg": "http://www.w3.org/2000/svg"}

        # Find the element with id="Hex0"
        vertex_element = self.root.find(f".//*[@id='Vertex{vertex.id}']", namespace)

        if vertex_element is not None:
            # Find the polygon inside the hex group
            polygon = vertex_element.find("svg:polygon", namespace)
            if polygon is not None:
                # Change the fill attribute
                if vertex.piece is not None:
                    color = vertex.piece.player.color
                else:
                    color = "transparent"
                polygon.set("fill", color)
            path = vertex_element.find("svg:path", namespace)
            if path is not None:
                if vertex.piece is None:
                    path.set("opacity", "0")
                else:
                    path.set("opacity", "1")

            else:
                raise ValueError(
                    f"Polygon not found inside element with id='Vertex{vertex.id}'"
                )
        else:
            raise ValueError(f"Element with id='Vertex{vertex.id}' not found")

    def set_hex_color(self, hexId: int, color: str) -> None:
        # Define the SVG namespace
        namespace = {"svg": "http://www.w3.org/2000/svg"}

        # Find the element with id="Hex0"
        hex_element = self.root.find(f".//*[@id='Hex{hexId}']", namespace)

        if hex_element is not None:
            # Find the polygon inside the hex group
            polygon = hex_element.find("svg:polygon", namespace)
            if polygon is not None:
                # Change the fill attribute
                polygon.set("fill", color)
            else:
                raise ValueError("Polygon not found inside element with id='Hex0'")
        else:
            raise ValueError("Element with id='Hex0' not found")
