import pygame
import pygame as pg
import pygame.draw as dr
import pygame.transform as tr
import pygame.sprite as spr
import sqlite3
import os
import sys

from functions import get_width, load_image
from widgets import Button, Image, Label, HorAlign, InputBox
from infowindow import InfoWindow
from main import MainWindow



class Settings:
    def __init__(self):
        # Задаём атрибуты:
        self.db = sqlite3.connect('DataBases/Reflection_db.db3')
        self.cur = self.db.cursor()
        self.FPS = 80
        self.size = (self.w, self.h) = (900, 550)
        self.cursor_group = spr.Group()
        # Флаги:
        self.running = True

    def info(self):
        window = InfoWindow()
        window.run()
        self.running = False
        sys.exit()

    def return_MainWindow(self):
        window = MainWindow()
        window.run()
        self.running = False
        sys.exit()

    def music(self):
        if pg.mixer.music.get_busy():
            pg.mixer.music.pause()
        else:
            pg.mixer.music.unpause()

    def clear(self):
        self.cur.execute("""UPDATE user SET victories = 0, defeats = 0""")
        self.cur.execute("""DELETE FROM savings""")
        self.cur.execute("""UPDATE levels SET score = NULL, time = NULL, opened = NULL""")
        self.cur.execute("""UPDATE levels SET opened = 'True' WHERE id = 1""")
        self.db.commit()

    def run(self):
        pg.init()
        pygame.mixer.music.load("Sounds/main_fone.mp3")
        pygame.mixer.music.play(-1)
        # Местные переменные и константы:
        clock = pg.time.Clock()
        # Задаём параметры окну:
        pg.display.set_caption('Настройки')
        self.screen = pg.display.set_mode(self.size)
        im = load_image('Fone.png')
        fone = tr.scale(im, (get_width(im, self.h), self.h))
        self.screen.blit(fone, (0, 0))
        pg.mouse.set_visible(False)
        pg.display.set_icon(load_image('Reflection_logo.png'))
        # Создаём спрайты:
        self.cursor = spr.Sprite(self.cursor_group)
        self.cursor.image = load_image("cursor.png")
        self.cursor.rect = self.cursor.image.get_rect()
        # Создаём виджеты:
        self.input_text = InputBox(self, (450, 240, 300, 40), '', font_size=32)
        self.lebels = [Label(self, (250, 300, 100, 100), 'Музыка', main_color=pg.Color(224, 176, 255), font_size=50, alignment=HorAlign.CENTER),
                       Label(self, (150, 160, 200, 200), 'Введите новый ник:', main_color=pg.Color(255, 51, 255),
                             font_size=40, alignment=HorAlign.LEFT)]
        self.buttons = [Image(self, (820, 470, 70, 70), load_image('Info.png'), bord_color=pg.Color(100, 200, 255),
                              light_image=load_image('Info_light.png'), slot=self.info),
                        Image(self, (10, 10, 70, 70),
                              load_image('Return.png'),
                              slot=self.return_MainWindow,
                              light_image=load_image('Return_light.png'),
                              bord_color=pg.Color(181, 230, 29)),
                        Button(self, (560, 10, 330, 70), 'Стереть все результаты', main_color=pg.Color(255, 218, 20), slot=self.clear),
                        Button(self, (420, 320, 180, 60), 'Включить', main_color=pg.Color(255, 188, 217), text2='Выключить', slot=self.music)]
        # Основной цикл игры:
        while self.running:
            # Обработка событий:
            for event in pg.event.get():
                self.input_text.process_event(event)
                for lb in self.lebels:
                    lb.process_event(event)
                for but in self.buttons:
                    but.process_event(event)
                if event.type == pg.QUIT:
                    self.running = False
                if event.type == pg.MOUSEMOTION:
                    self.cursor.rect.topleft = event.pos
            # Отрисовка элементов:
            self.screen.blit(fone, (0, 0))
            for lbl in self.lebels:
                lbl.render()
            for bt in self.buttons:
                bt.render()
            self.input_text.render()
            if pg.mouse.get_focused():
                self.cursor_group.draw(self.screen)
            # Обновление экрана:
            clock.tick(self.FPS)
            pg.display.flip()
        pg.quit()



if __name__ == '__main__':
    set = Settings()
    set.run()