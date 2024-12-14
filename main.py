import argparse
import logging
from lib.gameplay.game import Game
from lib.gameplay.params import DEFAULT_PARAMETERS
from lib.logging.database import MongoLogger
from lib.robot.robot import Robot
from lib.visualizer.renderer import Renderer
from lib.visualizer.action_graph_visualizer import ActionGraphVisualizer
from typing import cast


def parse_log_level(level_str: str) -> int:
    level = getattr(logging, level_str.upper(), None)
    if not isinstance(level, int):
        raise argparse.ArgumentTypeError(f"Invalid log level: {level_str}")
    return level


def main():
    parser = argparse.ArgumentParser(description="Catan Simulator")

    parser.add_argument(
        "-e",
        "--experiment",
        type=lambda s: s.split(","),  # Split the input string by commas
        help="Comma-separated list of experiment names",
    )
    parser.add_argument(
        "-s",
        "--study-name",
        type=str,
        help="Name of the study to evaluate",
    )

    parser.add_argument(
        "--log-level",
        "-l",
        type=parse_log_level,
        default=logging.WARNING,  # Default level
        help="Set the logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)",
    )

    # Add the delay argument
    parser.add_argument(
        "--delay",
        "-d",
        type=float,  # Accepts a number (integer or float)
        default=0,  # Default value if not provided
        help="Delay in seconds before the script proceeds.",
    )

    subparsers = parser.add_subparsers(dest="command", required=False)

    # Add 'play' subcommand
    play_parser = subparsers.add_parser("play", help="Start a game")
    play_parser.add_argument(
        "--delay",
        "-d",
        type=float,
        required=False,
        default=0,
        help="Delay in milliseconds between each turn",
    )
    play_parser.add_argument(
        "--num_players",
        "-n",
        type=int,
        default=4,
        help="Number of players in the game.",
    )
    play_parser.add_argument(
        "--log-level",
        "-l",
        type=parse_log_level,
        default=logging.WARNING,  # Default level
        help="Set the logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)",
    )

    # Add 'setup' subcommand
    setup_parser = subparsers.add_parser("setup", help="Setup a game")
    setup_parser.add_argument(
        "--num_players",
        "-n",
        type=int,
        default=4,
        help="Number of players in the game.",
    )
    setup_parser.add_argument(
        "--log-level",
        "-l",
        type=parse_log_level,
        default=logging.INFO,  # Default level
        help="Set the logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)",
    )

    # add the visualize boolean flag
    setup_parser.add_argument(
        "--visualize",
        "-v",
        help="Visualize the action graphs",
    )

    args = parser.parse_args()

    MongoLogger.initialize()

    # Configure logger
    logger = logging.getLogger(__name__)
    logging.basicConfig(
        level=args.log_level, format="%(levelname)s %(name)s: %(message)s"
    )

    if args.experiment:
        for experiment in args.experiment:
            if experiment == "win_stats":
                from lib.experiments.win_stats import win_stats

                win_stats(100)
            elif experiment == "optimize_orange":
                from lib.experiments.optimize_orange import optimize_orange

                study_name = args.study_name

                if study_name is not None:
                    optimize_orange(100, mode="evaluate", study_name=study_name)
                else:
                    optimize_orange(1000)
            else:
                logger.error(f"Unknown experiment: {experiment}")

    # Handle the 'play' command
    if args.command == "play":
        game = Game(num_players=args.num_players, game_delay=args.delay)
        Renderer(game)
        game.play()
    if args.command == "setup":
        logging.basicConfig(level=logging.INFO)
        game = Game(
            num_players=args.num_players, game_delay=0, parameters=DEFAULT_PARAMETERS
        )
        renderer = Renderer(game)
        renderer.render()
        if args.visualize:
            for player in game.players:
                logger.info(f"Visualizing action graph for {player}")
                if cast(Robot, player).action_graph is None:
                    logger.warning(f"No action graph found for {player}")
                    continue
                action_graph_visualizer = ActionGraphVisualizer(
                    cast(Robot, player).action_graph,
                    game,
                    f"action_graph_{player.color}.html",
                )
                action_graph_visualizer.visualize()
        print("Starting game...")
        print("Press enter to step, or q to quit")
        continue_game = False
        while game.winning_player is None:
            if not continue_game:
                action = input()
                if action == "q":
                    break
                if action == "c":
                    continue_game = True
                game.step()
            else:
                game.step()


if __name__ == "__main__":
    main()
