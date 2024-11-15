from lib.gameplay.player import Player
from lib.robot.robot import Robot
from lib.gameplay.bank import Bank
from lib.gameplay.board import Board
from lib.gameplay.hex import ResourceType
from lib.gameplay.dice import Dice
from enum import Enum
from typing import Callable, Union

NUM_PLAYERS = 4

COLORS = ["red", "blue", "white", "orange"]

INITIAL_PLACEMENTS = {
    0: {
        "settlement": [10, 29],
        "road": [13, 41],
        "resources": [ResourceType.WHEAT, ResourceType.WOOD, ResourceType.WOOD],
    },
    1: {
        "settlement": [44, 40],
        "road": [52, 56],
        "resources": [ResourceType.WOOD, ResourceType.ORE, ResourceType.BRICK],
    },
    2: {
        "settlement": [35, 19],
        "road": [25, 37],
        "resources": [ResourceType.WHEAT, ResourceType.WOOD, ResourceType.BRICK],
    },
    3: {
        "settlement": [13, 42],
        "road": [15, 58],
        "resources": [ResourceType.WHEAT, ResourceType.WHEAT, ResourceType.ORE],
    },
}


class GameEvent(Enum):
    START_GAME = "START_GAME"
    ROLL_DICE = "ROLL_DICE"
    BUILD_SETTLEMENT = "BUILD_SETTLEMENT"
    BUILD_ROAD = "BUILD_ROAD"
    BUILD_CITY = "BUILD_CITY"
    TRADE = "TRADE"
    END_TURN = "END_TURN"


class Game:
    def __init__(self):
        self.current_player: int = 0
        self.winning_player: Union[Player, None] = None
        self.bank = Bank()
        self.board = Board()
        self.dice = Dice()
        self.players = self.setup_players(NUM_PLAYERS)
        self.listeners = []

    def listen(self, callback: Callable[[GameEvent], None]) -> None:
        self.listeners.append(callback)

    def notify(self, event: GameEvent) -> None:
        for listener in self.listeners:
            listener(event)

    def setup_players(self, num_players: int) -> list[Player]:
        players = []
        for i in range(num_players):
            player = Robot(i, COLORS[i])
            players.append(player)

            for resource in INITIAL_PLACEMENTS[i]["resources"]:
                player.resources.append(self.bank.get_card(resource))

            for settlement in INITIAL_PLACEMENTS[i]["settlement"]:
                self.board.place_settlement(player, settlement)

            for road in INITIAL_PLACEMENTS[i]["road"]:
                self.board.place_road(player, road)
        return players

    def get_current_player(self) -> Player:
        return self.players[self.current_player]

    def get_player_by_color(self, color: str) -> Player:
        for player in self.players:
            if player.color == color:
                return player
        raise ValueError("Player not found")

    def step(self):
        curr_player = self.get_current_player()

        for player in self.players:
            print(f"{player} has {player.points(self.players)} points")

        print(f"{curr_player}'s turn")
        self.dice.roll()
        self.notify(GameEvent.ROLL_DICE)
        print(f"Dice roll: {self.dice.total}")

        if self.dice.total == 7:
            for player in self.players:
                if len(player.resources) > 7:
                    player.split_cards(self.bank)
        else:
            for player in self.players:
                print(f"{player} has {len(player.resources)} resources")
                player.collect_resources(self.bank, self.dice.total)
        curr_player.take_turn(self.board, self.bank, self.players)

        self.notify(GameEvent.END_TURN)

        if curr_player.points(self.players) >= 10:
            self.winning_player = curr_player

        self.current_player = (self.current_player + 1) % NUM_PLAYERS

    def play(self):
        self.notify(GameEvent.START_GAME)
        self.current_player = 0

        for player in self.players:
            for road in player.roads:
                print(road)

        while self.winning_player is None:
            self.step()
            # TODO: Implement end game condition
            self.winning_player = self.get_current_player()

        print(f"{self.winning_player} wins!")
