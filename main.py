import pygame as pg
import pygame.draw as dr
from datetime import time as Time


class Game:
    def __init__(self, csv_model_name, score, time):
        pass

    def run(self):
        pass

    def render(self):
        pass


class MainWindow:
    pass


if __name__ == '__main__':
    time = Time(minute=0, second=0)
    window = Game('DataBases/Level1_StartModel.csv', 0, time)
    window.run()
