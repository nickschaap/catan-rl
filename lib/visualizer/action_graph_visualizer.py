from lib.robot.action_graph import ActionGraph
from lib.gameplay.game import Game, GameEvent
import logging

logger = logging.getLogger(__name__)


class ActionGraphVisualizer:
    def __init__(
        self,
        action_graph: ActionGraph,
        game: Game,
        output_file: str = "action_graph.html",
    ):
        self.action_graph = action_graph
        self.game = game
        self.game.listen(self.on_game_event)
        self.output_file = output_file

    def on_game_event(self, event: GameEvent):
        if event == GameEvent.END_TURN:
            self.visualize()

    def visualize(self):
        logger.info(f"Visualizing action graph for {self.action_graph.player}")
        with open(self.output_file, "w") as f:
            html = "<html><head><link rel='stylesheet' href='index.css' /></head><body><script src='/livereload.js'></script>"
            html += "<div style='display: flex; justify-content: space-between;'>"
            html += "<a href='/'>Back</a>"
            html += "<a href='/red'>Red</a>"
            html += "<a href='/blue'>Blue</a>"
            html += "<a href='/orange'>Orange</a>"
            html += "<a href='/white'>White</a>"
            html += "</div>"
            html += f"<h1>Action Graph for {self.action_graph.player}</h1>"
            html += "<h2>Stats</h2>"
            html += f"{self.action_graph.get_state()}"
            html += "<h2>Actions</h2>"
            html += "<ul>"
            actions = self.action_graph.get_actions()
            for action in actions:
                html += f"<li>{action}</li>"
            html += "</ul></body></html>"
            f.write(html)
