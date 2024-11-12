import random


class Dice:
    def __init__(self):
        self.total = 0
        self.dice = [0, 0]

    def roll(self):
        self.dice[0] = random.randint(1, 6)
        self.dice[1] = random.randint(1, 6)
        self.total = self.get_sum()
        return self.dice

    def get_sum(self) -> int:
        return sum(self.dice)

    def get_dice(self) -> list[int]:
        return self.dice
