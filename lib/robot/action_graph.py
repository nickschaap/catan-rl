from typing import TYPE_CHECKING


from lib.robot.build_city import BuildCity
from lib.robot.buy_development_card import BuyDevelopmentCard
from lib.robot.build_settlement import BuildSettlement
from lib.robot.action import Action
from lib.robot.build_road import BuildRoad
from lib.robot.player_state import PlayerState

if TYPE_CHECKING:
    from lib.gameplay.player import Player
    from lib.gameplay.game import Game, GameEvent

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


class ActionGraph:
    def __init__(self, player: "Player", game: "Game"):
        self.player = player
        self.game = game
        self.player_state = PlayerState(self.player)
        self.game.listen(self.on_game_event)

    def on_game_event(self, event: "GameEvent") -> None:
        if str(event) == "GameEvent.START_TURN":
            if self.player.id == self.game.current_player:
                self.player_state.refresh_state()

    def execute_actions(self) -> None:
        actions = self.get_actions()
        for action in actions:
            if action.can_execute(self.game.board, self.game.bank, self.player):
                action.execute(
                    self.game.board, self.game.bank, self.player, self.game.players
                )

    def get_state(self) -> str:
        info = {
            "Resources": [
                str(k) + ": " + str(v)
                for k, v in self.player_state.resource_counts.items()
            ],
            "Settlements": [str(s.position) for s in self.player_state.settlements],
            "Cities": [str(c.position) for c in self.player_state.cities],
            "Roads": [str(r.position) for r in self.player_state.roads],
            "Resource Abundance": [
                str(k) + ": " + str(v)
                for k, v in self.player_state.resource_abundance.items()
            ],
        }

        state = "<ul>"
        for k, v in info.items():
            if len(v) > 1:
                state += (
                    f"<li>{k}: <ul>{"".join([f"<li>{i}</li>" for i in v])}</ul></li>"
                )
            else:
                state += f"<li>{k}: {v}</li>"
        state += "</ul>"
        return state

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

        return (
            settlement_actions
            + road_actions
            + city_actions
            + [BuyDevelopmentCard(self)]
        )
