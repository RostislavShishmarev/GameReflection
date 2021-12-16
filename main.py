import pygame as pg
import pygame.draw as dr
import csv
from datetime import time as Time


def do_nothing():
    pass


class Button:
    def __init__(self, parent, x, y, w, h, text, font_size=40,
                 main_color=pg.Color(70, 202, 232),
                 back_color=pg.Color(0, 0, 0), slot=do_nothing):
        self.parent = parent
        self.x, self.y, self.x1, self.y1 = x, y, x + w, y + h
        self.w, self.h = w, h
        self.text = text
        self.font_size = font_size
        self.main_color = main_color
        self.back_color = back_color
        self.slot = slot

    def render(self):
        screen = self.parent.screen
        dr.rect(screen, self.back_color,
                (self.x, self.y, self.w, self.h))
        dr.rect(screen, self.main_color,
                (self.x, self.y, self.w, self.h), width=2)
        font = pg.font.Font(None, self.font_size)
        text = font.render(self.text, True, self.main_color)
        screen.blit(text, (self.x + self.w // 2 - text.get_width() // 2,
                           self.y + self.h // 2 - text.get_height() // 2))


    def __contains__(self, item):
        return item[0] in range(self.x, self.x1) and\
               item[1] in range(self.y, self.y1)


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
        self.size = (self.w, self.h) = (1210, 820)
        self.left = 20
        self.top = 140
        self.cell_width = 90
        self.cell_height = 50
        self.pause = False
        self.running = True
        self.buttons = [Button(self, 20, self.h - 70, 350, 50,
                               'Сохранить', slot=self.save),
                        Button(self, self.w // 2 - 175, self.h - 70, 350, 50,
                               'Пауза', slot=self.change_pause),
                        Button(self, self.w - 370, self.h - 70, 350, 50,
                               'Выход', slot=self.exit)]

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
        while self.running:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.running = False
                if event.type == pg.MOUSEBUTTONDOWN:
                    for but in self.buttons:
                        if event.pos in but:
                            but.slot()
            self.screen.fill(pg.Color(31, 30, 38))
            self.render()
            for but in self.buttons:
                but.render()
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

    def change_pause(self):
        self.pause = not self.pause
        print('Pause changed.')

    def exit(self):
        print('Exit.')

    def save(self):
        print('Saved.')


class MainWindow:
    pass


if __name__ == '__main__':
    window = Game('DataBases/Level1_StartModel.csv')
    window.run()
