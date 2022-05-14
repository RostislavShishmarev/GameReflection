import csv
import sqlite3
from math import ceil

import pygame as pg
import pygame.draw as dr
from widgets import Button

from Modules.functions import load_image


# Предназначен только для разработки.
class LevelMaker:
    """Класс для создания уровней.
    Добавить блок - наведение на клетку + <клавиша>:
    b - обычный блок,
    k - кирпичный,
    s - скандиевый,
    e - взрывающийся,
    d - убивающий,
    любая другая - удаление блока."""
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
        self.button = Button(self, (width // 2 - but_w // 2,
                                    height - 5 - but_h, but_w, but_h),
                             'Сохранить', slot=self.save)
        self.db = sqlite3.connect('../DataBases/Reflection_db.db3')

    def render(self, screen):
        x, y = self.left, self.top
        for i, row in enumerate(self.board):
            for j, el in enumerate(row):
                if self.board[i][j] != 'nothing':
                    im = pg.transform.scale(load_image(self.board[i][j]),
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
        name = '../DataBases/Level' + n + '_StartModel.csv'
        with open(name, mode='w', encoding='utf8', newline='') as f:
            wr = csv.writer(f, delimiter=';', quotechar='"')
            for row in self.board:
                wr.writerow(row)
        print('Введите название уровня:')
        cur = self.db.cursor()
        cur.execute('''INSERT INTO levels(name, way) VALUES(?, ?)''',
                    (input(), name))
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
