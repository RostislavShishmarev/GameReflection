import pygame as pg
import pygame.transform as tr
import pygame.sprite as spr
import sqlite3

from functions import load_image, do_nothing, get_width
from widgets import Button, Image, Label, ScrollList, ResultsTextDisplay
from gamewindow import GameWindow


class MainWindow:
    def __init__(self):
        # Задаём атрибуты:
        self.FPS = 80
        self.size = (self.w, self.h) = (1300, 760)
        self.indent = 15

        self.db = sqlite3.connect('DataBases/Reflection_db.db3')
        cur = self.db.cursor()
        levels = cur.execute('''SELECT name, way, score, time
 FROM levels''').fetchall()
        self.levels = [(lv[0], lv[1:]) for lv in levels]
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
        self.levels_widget.set_elements(self.levels,
                                        select_func=self.update_window)

        self.savings_widget = ScrollList(self, (self.indent * 2 + levels_w,
                                                user_h + user_font +\
                                                self.indent * 3,
                                                self.w - self.indent * 3 -\
                                                levels_w, self.h - user_h -\
                                                user_font - self.indent *\
                                                6 - play_h), 'Сохранения')

        res_w = (self.w - self.indent * 4 - levels_w - but_h) // 2
        self.results = ResultsTextDisplay(self, (self.indent * 2 +\
                                                 levels_w + res_w,
                                                 self.indent, res_w,
                                                 user_h + user_font))

        # Основной цикл игры:
        while self.running:
            # Обработка событий:
            for event in pg.event.get():
                for but in self.buttons:
                    but.process_event(event)
                self.levels_widget.process_event(event)
                self.savings_widget.process_event(event)
                if event.type == pg.QUIT:
                    self.running = False
                if event.type == pg.MOUSEMOTION:
                    self.cursor.rect.topleft = event.pos

            # Отрисовка элементов:
            self.screen.blit(fone, (0, 0))
            for widget in self.buttons + self.user_widgets:
                widget.render()
            self.levels_widget.render()
            self.savings_widget.render()
            self.results.render()
            if pg.mouse.get_focused():
                self.cursor_group.draw(self.screen)

            # Обновление экрана:
            clock.tick(self.FPS)
            pg.display.flip()
        pg.quit()
        if self.new_window_after_self is not None:
            self.new_window_after_self.run()

    def update_window(self):
        try:
            cur = self.db.cursor()
            savings = cur.execute('''SELECT saving_time, model_way, score,
 time, lifes FROM savings WHERE level_index =
 ?''',(self.levels_widget.get_selected_item_index() + 1, )).fetchall()
            self.savings_widget.set_elements([(sav[0], sav[1:])
                                              for sav in savings])
        except TypeError as ex:
            self.savings_widget.set_elements([])
        records = self.levels_widget.get_selected_item_info()
        print(records)
        if records is not None:
            score, time = records[1:]
            if score is not None and time is not None:
                time = (int(time.split()[0]), int(time.split()[1]))
                self.results.set_records(score, time)
            else:
                self.results.set_records()

    def exit(self):
        self.running = False

    def open_settings(self):
        print('Opened')

    def open_gamewindow(self):
        saving = self.savings_widget.get_selected_item_info()
        if saving is None:
            level = self.levels_widget.get_selected_item_info()
            if level is not None:
                self.exit()
                self.new_window_after_self = GameWindow(self, level[0])
            return
        model, score, time, lifes = saving
        time = (int(time.split()[0]), int(time.split()[1]))
        self.exit()
        self.new_window_after_self = GameWindow(self, model, score,
                                                time, lifes)


if __name__ == '__main__':
    window = MainWindow()
    window.run()
