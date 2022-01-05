import pygame
import pygame as pg
import pygame.draw as dr
import pygame.transform as tr
import pygame.sprite as spr
import sqlite3
import os
import sys

from functions import do_nothing, get_width, load_image, str_time, get_max_font_size
from widgets import Button, Image, Label, BaseWidget, HorAlign, ScrollElement
from gamewindow import GameWindow
from infowindow import InfoWindow
from main import MainWindow

def print_text(display, message, x, y, font_color = (255, 255, 255), font_size=30):
    font_type = pygame.font.Font(None, font_size)
    text = font_type.render(message, True, font_color)
    display.blit(text, (x, y))

class Settings:
    def __init__(self):
        # Задаём атрибуты:
        self.FPS = 80
        self.size = (self.w, self.h) = (1100, 650)
        self.cursor_group = spr.Group()
        # Флаги:
        self.play = True
        self.running = True
        self.need_input = False
        self.input_text = ''

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

    def on_off(self):
        self.play = False

    def clear(self):
        pass

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
        self.lebels = [Label(self, (350, 400, 100, 100), 'Музыка', main_color=pg.Color(224, 176, 255), font_size=50, alignment=HorAlign.CENTER),
                      Label(self, (10, 10, 500, 200), '')]# main_color=()))]
        self.buttons = [Image(self, (1020, 570, 70, 70), load_image('Info.png'), bord_color=pg.Color(100, 200, 255),
                              light_image=load_image('Info_light.png'), slot=self.info),
                        Image(self, (10, 10, 70, 70),
                              load_image('Return.png'),
                              slot=self.return_MainWindow,
                              light_image=load_image('Return_light.png'),
                              bord_color=pg.Color(181, 230, 29)),
                        Button(self, (760, 10, 330, 70), 'Стереть все результаты', main_color=pg.Color(255, 218, 20), slot=self.clear),
                        Button(self, (520, 420, 180, 60), 'Включить', main_color=pg.Color(255, 188, 217), text2='Выключить', slot=self.on_off)]
        # Основной цикл игры:
        while self.running:
            # Обработка событий:
            for event in pg.event.get():
                for lb in self.lebels:
                    lb.process_event(event)
                for but in self.buttons:
                    but.process_event(event)
                if event.type == pg.QUIT:
                    self.running = False
                if self.play == True:
                    pygame.mixer.music.unpause()
                else:
                    pygame.mixer.music.pause()
                if event.type == pg.MOUSEMOTION:
                    self.cursor.rect.topleft = event.pos
                if self.need_input and event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        self.need_input = False
                        self.input_text = ''
                    elif event.key == pygame.K_BACKSPACE:
                        pass
                    else:
                        self.input_text += event.unicode
                keys = pg.key.get_pressed()
                if keys[pg.K_TAB]:
                    self.need_input = True
            # Отрисовка элементов:
            self.screen.blit(fone, (0, 0))
            for lbl in self.lebels:
                lbl.render()
            for bt in self.buttons:
                bt.render()
            if pg.mouse.get_focused():
                self.cursor_group.draw(self.screen)
            keys = pg.key.get_pressed()
            if keys[pg.K_TAB]:
                self.need_input = True
            print_text(self.screen, self.input_text, 100, 100)
            # Обновление экрана:
            clock.tick(self.FPS)
            pg.display.flip()
        pg.quit()



if __name__ == '__main__':
    set = Settings()
    set.run()