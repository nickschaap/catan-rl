from lib.gameplay import Game
from lib.visualizer import Renderer


def main():
    game = Game()
    renderer = Renderer(game)
    game.play()


if __name__ == "__main__":
    main()
