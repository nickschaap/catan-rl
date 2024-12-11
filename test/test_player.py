import pytest

from lib.gameplay.player import Player


@pytest.mark.player
def test_player() -> None:
    player = Player(0, "red")

    assert player.id == 0
    assert player.color == "red"
    assert str(player) == "Player red"
    assert hash(player) == 0

    assert len(player.cities) == 4
    assert len(player.settlements) == 5
    assert len(player.roads) == 15

    assert player.largest_army_size() == 0
    assert player.points(None, None) == 0
    assert player.get_active_settlements() == []
