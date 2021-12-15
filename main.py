import pygame as pg
import pygame.draw as dr
import csv
from datetime import time as Time


class Game:
    def __init__(self, csv_model_name, score=0, time=Time(), lifes=4):
        # Задаём атрибуты:
        self.blocks_dict = {'nothing': None}
        self.block_code_dict = {None: 'nothing'}

        self.mod_name = csv_model_name
        self.score = score
        self.time = time
        self.lifes = lifes

        self.FPS = 40
        self.size = (self.width, self.height) = (1240, 800)
        self.left = 20
        self.top = 140
        self.cell_width = 100
        self.cell_height = 60

        # Открываем модель расположения блоков:
        with open(self.mod_name, encoding='utf8') as model:
            self.blocks = [[self.blocks_dict[b] for b in row]
                           for row in list(csv.reader(model, delimiter=';'))]

    def run(self):
        pg.init()
        # Местные переменные и константы:
        clock = pg.time.Clock()

        # Задаём параметры окну:
        pg.display.set_caption('Отражение')
        self.screen = pg.display.set_mode(self.size)
        self.screen.fill(pg.Color(31, 30, 38))

        # Основной цикл игры:
        running = True
        while running:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False
            self.screen.fill(pg.Color(31, 30, 38))
            self.render()
            clock.tick(self.FPS)
            pg.display.flip()
        pg.quit()

    def render(self):
        x, y = self.left, self.top
        for i, row in enumerate(self.blocks):
            for j, el in enumerate(row):
                dr.rect(self.screen, pg.Color('white'), (x, y, self.cell_width,
                                                         self.cell_height),
                        width=2)  # Временно для проверки
                x += self.cell_width
            y += self.cell_height
            x = self.left


class MainWindow:
    pass


if __name__ == '__main__':
    window = Game('DataBases/Level1_StartModel.csv')
    window.run()
