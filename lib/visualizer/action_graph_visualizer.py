from lib.robot.action_graph import ActionGraph
from lib.gameplay.game import Game, GameEvent
import os


class ActionGraphVisualizer:
    def __init__(self, action_graph: ActionGraph, game: Game):
        self.action_graph = action_graph
        self.game = game
        self.game.listen(self.onGameEvent)
        self.output_file = os.path.join("action_graph.html")

    def onGameEvent(self, event: GameEvent):
        if event == GameEvent.END_TURN:
            self.visualize()

    def visualize(self):
        print("Visualizing action graph")
        with open(self.output_file, "w") as f:
            html = "<html><body>"
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
