import math


def normalize(x: float) -> float:
    return 2 * (1 / (1 + math.exp(-x)) - 0.5)


def sigmoid(x: float) -> float:
    return 1 / (1 + math.exp(-x))


def lerp(a: float, b: float, t: float) -> float:
    """A function that returns a number between 0 and 1 indicating how close t is to a or b"""
    return (t - a) / ((b - a) + 0.1)
