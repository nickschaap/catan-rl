import argparse
import logging
from lib.gameplay.game import Game
from lib.visualizer.renderer import Renderer


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
        required=True,
        help="Delay in seconds before starting the game.",
    )
    play_parser.add_argument(
        "--num_players",
        "-n",
        type=int,
        default=4,
        help="Number of players in the game.",
    )

    # Add 'play' subcommand
    setup_parser = subparsers.add_parser("setup", help="Setup a game")
    setup_parser.add_argument(
        "--num_players",
        "-n",
        type=int,
        default=4,
        help="Number of players in the game.",
    )

    args = parser.parse_args()

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
            else:
                logger.error(f"Unknown experiment: {experiment}")
    # Handle the 'play' command
    if args.command == "play":
        game = Game(num_players=args.num_players, game_delay=args.delay)
        Renderer(game)
        game.play()
    if args.command == "setup":
        game = Game(num_players=args.num_players, game_delay=args.delay)
        renderer = Renderer(game)
        renderer.render()


if __name__ == "__main__":
    main()
