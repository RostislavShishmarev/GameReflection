import pygame as pg
import pygame.transform as tr
import pygame.sprite as spr

from functions import load_image, do_nothing, get_width
from widgets import TabWidget, TextDisplay, Image


class InfoWindow:
    def __init__(self):
        # Задаём атрибуты:
        self.FPS = 60
        self.size = (self.w, self.h) = (1400, 800)
        self.indent = 15
        self.up_indent = 60

        self.cursor_group = spr.Group()

        # Флаги:
        self.running = True
        self.new_window_after_self = None

    def run(self):
        pg.init()
        # Местные переменные и константы:
        clock = pg.time.Clock()

        # Задаём параметры окну:
        pg.display.set_caption('Отражение: правила')
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
        self.buttons = [Image(self, (self.w - self.indent - self.up_indent,
                                     self.indent,
                                     self.up_indent, self.up_indent),
                              load_image('Exit.png'),
                              slot=self.exit,
                              light_image=load_image('Exit_light.png'),
                              bord_color=pg.Color(70, 202, 232),
                              key=pg.K_HOME, modifier=pg.KMOD_CTRL)]
        self.tab_widget = TabWidget(self, (self.indent,
                                           self.indent * 2 + self.up_indent,
                                           self.w - self.indent * 2,
                                           self.h - self.indent * 3 -\
                                           self.up_indent),
                                    ['Основные правила', 'Блоки', 'Сокровища'])
        self.tab_widget.set_widgets(0, [TextDisplay(self, (50, 50, 400, 100),
                                                    'qwerty', 'boom!')])

        # Основной цикл игры:
        while self.running:
            # Обработка событий:
            for event in pg.event.get():
                self.tab_widget.process_event(event)
                for but in self.buttons:
                    but.process_event(event)
                if event.type == pg.QUIT:
                    self.running = False
                if event.type == pg.MOUSEMOTION:
                    self.cursor.rect.topleft = event.pos

            # Отрисовка элементов:
            self.screen.blit(fone, (0, 0))
            self.tab_widget.render()
            for but in self.buttons:
                but.render()
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


if __name__ == '__main__':
    window = InfoWindow()
    window.run()
