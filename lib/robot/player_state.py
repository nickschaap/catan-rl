from typing import TYPE_CHECKING
import logging

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from lib.gameplay.player import Player


class PlayerState:
    def __init__(self, player: "Player"):
        self.player = player
        self.refresh_state()

    def refresh_state(self) -> None:
        logger.info(f"Refreshing state for {self.player}")
        self.resource_counts = self.player.resource_counts()
        self.resource_abundance = self.player.resource_abundance()
        self.purchase_power = self.player.purchase_power()
        self.resource_importance = self.player.resource_importance()
        self.settlements = self.player.get_active_settlements()
        self.cities = self.player.get_active_cities()
        self.roads = self.player.get_active_roads()

    def __str__(self) -> str:
        info = {
            "Resources": [
                str(k) + ": " + str(v) for k, v in self.resource_counts.items()
            ],
            "Settlements": [
                f"{s.position} ({", ".join([str(s) for s in s.get_resources()])})"
                for s in self.settlements
            ],
            "Cities": [str(c.position) for c in self.cities],
            "Roads": [str(r.position) for r in self.roads],
            "Resource Abundance": [
                str(k) + ": " + str(v) for k, v in self.resource_abundance.items()
            ],
            "Purchase Power": [
                str(k) + ": " + str(v) for k, v in self.purchase_power.items()
            ],
            "Resource Importance": [
                str(k) + ": " + str(v) for k, v in self.resource_importance.items()
            ],
            "Points": [self.player.points()],
            "Development Cards": [str(card) for card in self.player.development_cards],
            "Has Longest Road": [
                self.player.game.player_with_longest_road == self.player
            ],
            "Has Largest Army": [
                self.player.game.player_with_largest_army == self.player
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
