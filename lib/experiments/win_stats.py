from lib.gameplay import Game
from lib.gameplay.game import COLORS
from lib.visualizer import Renderer
import matplotlib.pyplot as plt
import matplotlib
import logging

matplotlib.rcParams["text.usetex"] = True
matplotlib.rcParams["font.family"] = "serif"  # Use a serif font like in LaTeX

logger = logging.getLogger(__name__)


def win_stats(num_games: int):
    results: list[str] = []
    for i in range(1, num_games + 1):
        game = Game()
        if i == num_games:
            Renderer(game)
        try:
            game.play()
        except Exception as e:
            logger.error(f"Game {i} failed: {e}")

        results.append(game.winning_player.color if game.winning_player else "none")
        logger.info(f"=======================Game {i} Done=======================")
    plot_results(results)


def plot_results(results: list[str]):
    # Count the occurrences of each result
    counts = {color: 0 for color in COLORS}
    for result in results:
        if result not in counts:
            counts[result] = 0
        counts[result] += 1

    # Separate the keys and values
    categories = list(counts.keys())
    values = list(counts.values())

    # Create bar chart
    plt.bar(categories, values)

    # Add title and labels
    plt.title("Win Rate")
    plt.xlabel("Player")
    plt.ylabel("Win Rate")

    # Show the plot
    plt.savefig("output/win_stats.png", dpi=300)
    plt.clf()
