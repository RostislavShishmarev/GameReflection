import pygame as pg
import pygame.draw as dr
from math import ceil
import os
import csv
import sqlite3


def load_image(name, color_key=None):
    fullname = os.path.join('../Images', name)
    try:
        image = pg.image.load(fullname)
    except pg.error as message:
        print('Cannot load image:', name)
        raise SystemExit(message)

    if color_key is not None:
        image = image.convert()
        if color_key == -1:
            color_key = image.get_at((0, 0))
        image.set_colorkey(color_key)
    else:
        image = image.convert_alpha()
    return image


def do_nothing():
    pass


class Button:
    def __init__(self, parent, x, y, w, h, text, font_size=40,
                 main_color=pg.Color(70, 202, 232),
                 back_color=pg.Color(0, 0, 0), slot=do_nothing, text2=None):
        self.parent = parent
        self.x, self.y, self.x1, self.y1 = x, y, x + w, y + h
        self.w, self.h = w, h
        self.text = text
        self.text2 = text2 if text2 is not None else text
        self.current_text = self.text
        self.font_size = font_size
        self.main_color = main_color
        self.light_main_color = main_color
        self.back_color = back_color
        self.num_of_change = 0  # Количество отображений до конца подсветки
        self.function = slot

    def slot(self):
        # Декорация переданной функции:
        self.current_text = self.text if self.current_text == self.text2\
            else self.text2
        self.light_main_color = pg.Color(min(self.main_color.r + 90, 255),
                                         min(self.main_color.g + 90, 255),
                                         min(self.main_color.b + 90, 255))
        self.num_of_change = 10

        self.function()

    def render(self):
        screen = self.parent.screen
        dr.rect(screen, self.back_color,
                (self.x, self.y, self.w, self.h))
        dr.rect(screen, self.light_main_color,
                (self.x, self.y, self.w, self.h), width=2)
        font = pg.font.Font(None, self.font_size)
        text = font.render(self.current_text, True, self.light_main_color)
        screen.blit(text, (self.x + self.w // 2 - text.get_width() // 2,
                           self.y + self.h // 2 - text.get_height() // 2))
        # Регулировка подсветки:
        if self.num_of_change == 0:
            self.light_main_color = self.main_color
        else:
            self.num_of_change -= 1

    def __contains__(self, item):
        return item[0] in range(self.x, self.x1) and\
               item[1] in range(self.y, self.y1)


class LevelMaker:
    def __init__(self, self_width, self_height, left=10, top=10, w=60, h=35):
        self.width = self_width
        self.height = self_height
        self.left = left
        self.top = top
        self.cell_width = w
        self.cell_height = h
        self.screen = screen
        self.board = [['nothing'] * self_width for _ in range(self_height)]

        self.border_color = pg.Color('grey')
        self.border_width = 1
        but_w, but_h = 160, 40
        self.button = Button(self, width // 2 - but_w // 2,
                             height - 5 - but_h, but_w, but_h,
                             'Сохранить', slot=self.save)
        self.db = sqlite3.connect('Reflection_db.db3')

    def render(self, screen):
        x, y = self.left, self.top
        for i, row in enumerate(self.board):
            for j, el in enumerate(row):
                if self.board[i][j] != 'nothing':
                    im = pg.transform.scale(load_image('../Images/' +\
                                                       self.board[i][j]),
                                                (self.cell_width,
                                                 self.cell_height))
                    screen.blit(im, (x, y))
                # Границы:
                dr.rect(screen, self.border_color, (x, y, self.cell_width,
                                                    self.cell_height),
                        width=self.border_width)
                x += self.cell_width
            y += self.cell_height
            x = self.left
        self.button.render()

    def get_cell(self, pos):
        x, y = pos
        x_out = x < self.left or x > self.left + self.width * self.cell_width
        y_out = y < self.top or y > self.top + self.height * self.cell_height
        if x_out or y_out:
            return None
        return (ceil((y - self.top) / self.cell_height) - 1,
                ceil((x - self.left) / self.cell_width) - 1)

    def on_click(self, cell_coords, key):
        i, j = cell_coords
        if key == pg.K_b:
            self.board[i][j] = 'Block.png'
        elif key == pg.K_k:
            self.board[i][j] = 'Bricked_block.png'
        elif key == pg.K_s:
            self.board[i][j] = 'Sc_block.png'
        elif key == pg.K_e:
            self.board[i][j] = 'Exploding_block.png'
        elif key == pg.K_d:
            self.board[i][j] = 'Death_block.png'
        else:
            self.board[i][j] = 'nothing'

    def get_click(self, key, pos):
        cell = self.get_cell(pos)
        if cell:
            self.on_click(cell, key)

    def save(self):
        print('Введите номер уровня:')
        n = input()
        name = 'Level' + n + '_StartModel.csv'
        with open(name, mode='w', encoding='utf8', newline='') as f:
            wr = csv.writer(f, delimiter=';', quotechar='"')
            for row in self.board:
                wr.writerow(row)
        print('Введите название уровня:')
        cur = self.db.cursor()
        cur.execute('''INSERT INTO levels(name, way) VALUES(?, ?)''',
                    (input(), 'DataBases/' + name))
        cur.execute('''INSERT INTO records(level_index) VALUES(?)''', (n, ))
        print('Сохранено.')
        self.db.commit()


if __name__ == '__main__':
    pg.init()
    Color = pg.Color
    clock = pg.time.Clock()
    fps = 30
    size = (width, height) = (800, 400)

    pg.display.set_caption('Уравнеделатель')
    screen = pg.display.set_mode(size)
    screen.fill(Color('black'))
    running = True
    board = LevelMaker(13, 9)
    pos = (0, 0)
    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            if event.type == pg.MOUSEMOTION:
                pos = event.pos
            if event.type == pg.KEYDOWN:
                board.get_click(event.key, pos)
            if event.type == pg.MOUSEBUTTONDOWN:
                if event.pos in board.button:
                    board.button.slot()
        screen.fill((0, 0, 0))
        board.render(screen)
        clock.tick(fps)
        pg.display.flip()
    pg.quit()
