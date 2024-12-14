from typing import TYPE_CHECKING, Literal, Union


from lib.gameplay.pieces import CardType
from lib.logging.database import MongoLogger
from lib.robot.build_city import BuildCity
from lib.robot.buy_development_card import BuyDevelopmentCard
from lib.robot.build_settlement import BuildSettlement
from lib.robot.action import Action
from lib.robot.build_road import BuildRoad
from lib.robot.play_development_card import PlayDevelopmentCard
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
        self.settlement_actions = []
        self.city_actions = []
        self.road_actions = []

    def on_game_event(self, event: "GameEvent") -> None:
        if str(event) == "GameEvent.START_TURN" or str(event) == "GameEvent.END_TURN":
            self.player_state.refresh_state()

    def log_actions(self, actions: list[Action]) -> None:
        for action in actions:
            MongoLogger.log(
                "action_logs",
                {
                    "game_id": self.game.game_id,
                    "turn_number": self.game.turn_number,
                    "player_id": self.player.id,
                    "action": str(action.action_type),
                    "cost": action.cost,
                    "reward": action.reward,
                    "priority": action.priority,
                    "can_execute": action.can_execute(
                        self.game.board, self.game.bank, self.player
                    ),
                    "player_resources": [
                        str(resource) for resource in self.player.resources
                    ],
                    "player_development_cards": [
                        str(card) for card in self.player.development_cards
                    ],
                    "player_settlements": [
                        str(settlement)
                        for settlement in self.player.get_active_settlements()
                    ],
                    "player_cities": [
                        str(city) for city in self.player.get_active_cities()
                    ],
                    "player_roads": [
                        str(road) for road in self.player.get_active_roads()
                    ],
                    "executed": action.executed,
                },
            )

    def execute_actions(
        self, stage: Union[Literal["pre_roll"], Literal["post_roll"]]
    ) -> None:
        actions = (
            self.get_post_roll_actions()
            if stage == "post_roll"
            else self.get_pre_roll_actions()
        )
        for action in actions:
            num_resources = len(self.player.resources)
            if (action.priority > 0 or num_resources > 7) and action.can_execute(
                self.game.board, self.game.bank, self.player
            ):
                action.execute(
                    self.game.board, self.game.bank, self.player, self.game.players
                )
        self.log_actions(actions)

    def get_state(self) -> str:
        return str(self.player_state)

    def get_pre_roll_actions(self) -> list[Action]:
        player = self.player

        actions = []

        robber_loc = self.game.board.robberLoc
        settled_hexes = player.get_settled_hexes()

        unflipped_knights = [
            card
            for card in player.development_cards
            if card.cardType == CardType.KNIGHT and card.flipped is False
        ]

        if len(unflipped_knights) > 0 and any(
            hex.id == robber_loc and hex.resourceType is not None
            for hex in settled_hexes
        ):
            # Player is blocked and has knights to play
            actions.append(PlayDevelopmentCard(unflipped_knights[0], self))

        unflipped_victory_points = [
            card
            for card in player.development_cards
            if card.cardType == CardType.VICTORY_POINT and card.flipped is False
        ]

        if len(unflipped_victory_points) > 0:
            for card in unflipped_victory_points:
                actions.append(PlayDevelopmentCard(card, self))

        return actions

    def get_post_roll_actions(self) -> list[Action]:
        board = self.game.board
        self.settlement_actions = [
            BuildSettlement(vertex, self)
            for vertex in board.vertices
            if vertex.piece is None and board.can_settle(vertex.id)
        ]

        self.city_actions = [
            BuildCity(settlement.vertex, self)
            for settlement in self.player.get_active_settlements()
            if settlement.vertex is not None
        ]

        self.road_actions = [
            BuildRoad(edge, self) for edge in board.edges if edge.piece is None
        ]

        return sorted(
            self.settlement_actions
            + self.road_actions
            + self.city_actions
            + [BuyDevelopmentCard(self)],
            key=lambda x: x.priority,
            reverse=True,
        )
