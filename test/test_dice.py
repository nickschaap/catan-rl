import pytest
from lib.gameplay.dice import Dice


@pytest.mark.dice
def test_dice() -> None:
    """Check that the dice rolls are within the expected range"""
    dice = Dice()
    for _ in range(100):
        dice.roll()
        assert 2 <= dice.total <= 12
        assert 1 <= dice.dice[0] <= 6
        assert 1 <= dice.dice[1] <= 6
        assert dice.total == sum(dice.dice)
        assert dice.get_dice() == [dice.dice[0], dice.dice[1]]
