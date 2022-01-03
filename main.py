import pygame as pg
import pygame.transform as tr
import pygame.sprite as spr
import sqlite3

from functions import load_image, do_nothing, get_width
from widgets import Button, Image, Label, ScrollList


class MainWindow:
    def __init__(self):
        # Задаём атрибуты:
        self.FPS = 80
        self.size = (self.w, self.h) = (1300, 760)
        self.indent = 15

        self.db = sqlite3.connect('DataBases/Reflection_db.db3')
        cur = self.db.cursor()
        levels = cur.execute('''SELECT name, way FROM levels''').fetchall()
        self.levels = [(lv[0], [lv[1], ]) for lv in levels]
        self.nik = cur.execute('''SELECT nik FROM user''').fetchone()[0]
        self.photo_index = 0
        self.photos_names = ['User_cat.jpg']

        self.cursor_group = spr.Group()

        # Флаги:
        self.running = True
        self.new_window_after_self = None

    def run(self):
        pg.init()
        # Местные переменные и константы:
        clock = pg.time.Clock()

        # Задаём параметры окну:
        pg.display.set_caption('Отражение')
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
        photo = load_image(self.photos_names[self.photo_index])
        user_h = 130
        user_font = 40
        self.user_widgets = [Image(self, (self.indent, self.indent,
                                       user_h, user_h),
                                photo, bord_color=pg.Color(35, 81, 247)),
                             Label(self, (self.indent,
                                          self.indent + user_h,
                                          2 * user_h, user_font),
                                self.nik, font_size=user_font)]
        but_h = 90
        play_h = 70
        play_w = 200
        self.buttons = [Image(self, (self.w - self.indent - but_h,
                                     self.indent, but_h, but_h),
                              load_image('Settings.png', -1),
                              light_image=load_image('Settings_light.png', -1),
                              slot=self.open_settings),
                        Button(self, (self.w - 2 * self.indent - play_h - play_w,
                                      self.h - self.indent - play_h, play_w,
                                      play_h), 'Играть',
                               slot=self.open_gamewindow, font_size=60),
                        Image(self, (self.w - self.indent - play_h,
                                     self.h - self.indent - play_h,
                                     play_h, play_h), load_image('Exit.png'),
                              light_image=load_image('Exit_light.png'),
                              bord_color=pg.Color(70, 202, 232),
                              slot=self.exit)]

        levels_w = 350
        self.levels_widget = ScrollList(self, (self.indent,
                                        user_h + user_font + self.indent * 3,
                                        levels_w,
                                        self.h - user_h - user_font -\
                                        self.indent * 4), 'Уровни',
                                 n_vizible=7)
        self.levels_widget.set_elements(self.levels)

        # Основной цикл игры:
        while self.running:
            # Обработка событий:
            for event in pg.event.get():
                for but in self.buttons:
                    but.process_event(event)
                self.levels_widget.process_event(event)
                if event.type == pg.QUIT:
                    self.running = False
                if event.type == pg.MOUSEMOTION:
                    self.cursor.rect.topleft = event.pos

            # Отрисовка элементов:
            self.screen.blit(fone, (0, 0))
            for widget in self.buttons + self.user_widgets:
                widget.render()
            self.levels_widget.render()
            if pg.mouse.get_focused():
                self.cursor_group.draw(self.screen)

            # Обновление элементов:
            clock.tick(self.FPS)
            pg.display.flip()
        pg.quit()
        if self.new_window_after_self is not None:
            self.new_window_after_self.run()

    def exit(self):
        self.running = False

    def open_settings(self):
        print('Opened')

    def open_gamewindow(self):
        print('Game opened')


if __name__ == '__main__':
    window = MainWindow()
    window.run()
