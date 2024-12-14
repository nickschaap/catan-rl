from typing import Union
from lib.gameplay import Game
from lib.gameplay.game import COLORS
from lib.gameplay.params import DEFAULT_PARAMETERS, GameParameters
from lib.logging.database import MongoLogger
from lib.visualizer import Renderer
import matplotlib.pyplot as plt
import matplotlib
import logging
import os
import uuid

matplotlib.rcParams["text.usetex"] = True
matplotlib.rcParams["font.family"] = "serif"  # Use a serif font like in LaTeX

logger = logging.getLogger(__name__)

logger.setLevel(logging.INFO)


def win_stats(
    num_games: int, parameters: Union[list[GameParameters], None] = None
) -> None:
    results: list[str] = []
    turn_counts: list[int] = []
    experiment_id = str(uuid.uuid4())
    for i in range(1, num_games + 1):
        game = Game(
            experiment_id=experiment_id, parameters=parameters or DEFAULT_PARAMETERS
        )
        if i == num_games:
            Renderer(game)
        try:
            game.play()
            logger.info(f"Game {i} done: {game.winning_player} won")
            turn_counts.append(game.turn_number)
        except Exception as e:
            logger.error(f"Game {i} failed: {e}")

        results.append(game.winning_player.color if game.winning_player else "none")
        logger.info(f"=======================Game {i} Done=======================")
    plot_results(results, experiment_id)


def plot_results(results: list[str], id: str):
    # Count the occurrences of each result
    counts = {color: 0 for color in COLORS}

    for result in results:
        if result not in counts:
            counts[result] = 0
        counts[result] += 1
    MongoLogger.log("win_stats", {**counts, "experiment_id": id})

    # Separate the keys and values
    categories = list(counts.keys())
    values = list(counts.values())

    # Create bar chart
    plt.bar(categories, values)

    # Add title and labels
    plt.title("Win Rate")
    plt.xlabel("Player")
    plt.ylabel("Win Rate")

    # Make dir if it doesn't exist
    os.makedirs("output", exist_ok=True)

    # Show the plot
    plt.savefig(f"output/win_stats_{id}.png", dpi=300)
    plt.clf()
    logger.info(f"Saved plot to output/win_stats_{id}.png")
