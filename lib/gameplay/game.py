from lib.gameplay.player import Player
from lib.robot.robot import Robot
from lib.gameplay.bank import Bank
from lib.gameplay.board import Board
from lib.gameplay.hex import ResourceType
from lib.gameplay.dice import Dice
from enum import Enum
from typing import Callable, Union
import logging
import time

logger = logging.getLogger(__name__)

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
    def __init__(self, num_players: int = NUM_PLAYERS, game_delay: int = 0):
        self.current_player: int = 0
        self.turn_number: int = 0
        self.winning_player: Union[Player, None] = None
        self.bank = Bank(include_progress_cards=False)
        self.board = Board()
        self.dice = Dice()
        self.players = self.setup_players(num_players)
        self.num_players = num_players
        self.listeners = []
        self.game_delay = game_delay
        self.player_with_largest_army: Union["Player", None] = None
        self.player_with_longest_road: Union["Player", None] = None

    def listen(self, callback: Callable[[GameEvent], None]) -> None:
        self.listeners.append(callback)

    def notify(self, event: GameEvent) -> None:
        for listener in self.listeners:
            listener(event)

    def setup_players(self, num_players: int) -> list[Player]:
        players = []
        for i in range(num_players):
            player = Robot(i, COLORS[i], self)
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

    def get_player_with_longest_road(self) -> Union[Player, None]:
        player_with_longest_road = self.player_with_longest_road

        # Minimum length for longest road is greater than 4
        longest_road = (
            4
            if player_with_longest_road is None
            else self.board.longest_road(player_with_longest_road)
        )
        for player in self.players:
            if player == player_with_longest_road:
                continue
            road_length = self.board.longest_road(player)
            # Must be explicitly larger than the longest so far
            if road_length > longest_road:
                player_with_longest_road = player
                longest_road = road_length
        self.player_with_longest_road = player_with_longest_road
        return self.player_with_longest_road

    def get_player_with_largest_army(self) -> Union[Player, None]:
        player_with_largest_army = self.player_with_largest_army
        # Minimum length for largest army is greater than 3
        largest_army = (
            2
            if self.player_with_largest_army is None
            else self.player_with_largest_army.largest_army_size()
        )
        for player in self.players:
            if player == player_with_largest_army:
                continue
            army_size = player.largest_army_size()
            if army_size > largest_army:
                player_with_largest_army = player
                largest_army = army_size
        self.player_with_largest_army = player_with_largest_army
        return self.player_with_largest_army

    def step(self) -> bool:
        """Returns True if the game is over, False otherwise"""
        curr_player = self.get_current_player()
        playerWithLargestArmy = self.get_player_with_largest_army()
        playerWithLongestRoad = self.get_player_with_longest_road()
        for player in self.players:
            logger.info(
                f"{player} has {player.points(playerWithLongestRoad, playerWithLargestArmy)} points"
            )

        logger.info(f"{curr_player}'s turn")
        self.dice.roll()
        self.notify(GameEvent.ROLL_DICE)
        logger.info(f"Dice roll: {self.dice.total}")

        if self.dice.total == 7:
            for player in self.players:
                if len(player.resources) > 7:
                    player.split_cards(self.bank)
            curr_player.move_robber(self.board, self.bank)
        else:
            for player in self.players:
                logger.info(f"{player} has {len(player.resources)} resources")
                player.collect_resources(self.bank, self.dice.total)
        curr_player.take_turn(self.board, self.bank, self.players)

        self.notify(GameEvent.END_TURN)

        if curr_player.points(self.players, self.get_player_with_longest_road()) >= 10:
            self.winning_player = curr_player

        self.current_player = (self.current_player + 1) % self.num_players
        if self.game_delay > 0:
            time.sleep(self.game_delay / 1000)

        return self.winning_player is not None

    def play(self):
        self.notify(GameEvent.START_GAME)
        self.turn_number = 0

        while not self.step():
            self.turn_number += 1
            if self.turn_number == 100 * self.num_players:
                self.winning_player = self.get_current_player()
                logger.warning("Game ended in a draw")
        logger.info(f"{self.winning_player} wins in {self.turn_number} turns!")

        for player in self.players:
            logger.info(
                f"{player} has {player.points(self.players, self.get_player_with_longest_road())} points"
            )
            longest_road_player = self.get_player_with_longest_road()
            if longest_road_player is not None:
                logger.info(f"{longest_road_player} has longest road")
                logger.info(
                    f"Longest road length: {self.board.longest_road(longest_road_player)}"
                )
            logger.info(f"{player.resource_counts()}")
