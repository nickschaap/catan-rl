from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from lib.gameplay.player import Player


class PlayerState:
    def __init__(self, player: "Player"):
        self.player = player
        self.refresh_state()

    def refresh_state(self) -> None:
        self.resource_counts = self.player.resource_counts()
        self.resource_abundance = self.player.resource_abundance()
        self.settlements = self.player.get_active_settlements()
        self.cities = self.player.get_active_cities()
        self.roads = self.player.get_active_roads()

    def __str__(self) -> str:
        return f"{self.player.name} <ul>{''.join([f'<li>{k}: {v}</li>' for k, v in self.resource_counts.items()])}</ul>"
