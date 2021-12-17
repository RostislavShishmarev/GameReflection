import pygame as pg
import pygame.draw as dr
import csv
from datetime import datetime as DateTime
from datetime import timedelta as TimeDelta


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
        self.back_color = back_color
        self.function = slot

    def slot(self):
        # Декорация переданной функции:
        self.current_text = self.text if self.current_text == self.text2\
            else self.text2

        self.function()

    def render(self):
        screen = self.parent.screen
        dr.rect(screen, self.back_color,
                (self.x, self.y, self.w, self.h))
        dr.rect(screen, self.main_color,
                (self.x, self.y, self.w, self.h), width=2)
        font = pg.font.Font(None, self.font_size)
        text = font.render(self.current_text, True, self.main_color)
        screen.blit(text, (self.x + self.w // 2 - text.get_width() // 2,
                           self.y + self.h // 2 - text.get_height() // 2))

    def __contains__(self, item):
        return item[0] in range(self.x, self.x1) and\
               item[1] in range(self.y, self.y1)


class TextDisplay:
    def __init__(self, parent, x, y, w, h, title, text_item,
                 title_font_size=40, item_font_size=70,
                 main_color=pg.Color(239, 242, 46),
                 back_color=pg.Color(0, 0, 0), image=None):
        self.parent = parent
        self.x, self.y, self.x1, self.y1 = x, y, x + w, y + h
        self.w, self.h = w, h
        self.item = text_item
        self.title = title
        self.title_font_size = title_font_size
        self.item_font_size = item_font_size
        self.main_color = main_color
        self.back_color = back_color
        self.image = image

    def render(self):
        screen = self.parent.screen
        dr.rect(screen, self.back_color,
                (self.x, self.y, self.w, self.h), border_radius=8)
        dr.rect(screen, self.main_color,
                (self.x, self.y, self.w, self.h), width=2, border_radius=8)

        title_font = pg.font.Font(None, self.title_font_size)
        title = title_font.render(self.title, True, self.main_color)
        screen.blit(title, (self.x + self.w // 2 - title.get_width() // 2,
                           self.y + 5))

        item_font = pg.font.Font(None, self.item_font_size)
        item = item_font.render(self.item, True, self.main_color)
        item_x = self.x + self.w // 2 - item.get_width() // 2
        if self.image is not None:
            item_x = self.x + self.w - item.get_width() - 30
            # Загружаем картинку
        screen.blit(item, (item_x, self.y + self.h - item.get_height() - 5))

    def set_item(self, item):
        self.item = item


class Game:
    def __init__(self, parent, csv_model_name,
                 score=0, time=(0, 0), lifes=4):
        # Задаём атрибуты:
        self.blocks_dict = {'nothing': None}
        self.block_code_dict = {None: 'nothing'}

        self.parent = parent
        self.mod_name = csv_model_name
        self.score = score
        self.time = DateTime(2020, 1, 1, 1, *time)
        self.lifes = lifes

        self.FPS = 40
        self.size = (self.w, self.h) = (1210, 820)
        self.blocks_left = 20
        self.blocks_top = 140
        self.block_width = 90
        self.block_height = 50

        self.pause = False
        self.running = True
        self.start = True

        # Создаём виджеты:
        self.buttons = [Button(self, 20, self.h - 70, 350, 50,
                               'Сохранить', slot=self.save),
                        Button(self, self.w // 2 - 175, self.h - 70, 350, 50,
                               'Пауза', slot=self.change_pause,
                               text2='Продолжить'),
                        Button(self, self.w - 370, self.h - 70, 350, 50,
                               'Выход', slot=self.exit)]
        self.displays = [TextDisplay(self, 20, 20, 300, 100,
                                     'Очки', str(self.score)),
                         TextDisplay(self, self.w // 2 - 150, 20, 300, 100,
                                     'Жизни', str(self.lifes), image=0),
                         TextDisplay(self, self.w - 320, 20, 300, 100,
                                     'Время', self.time.strftime('%M:%S'))]

        # Открываем модель расположения блоков:
        with open(self.mod_name, encoding='utf8') as model:
            self.blocks = [[self.blocks_dict[b] for b in row]
                           for row in list(csv.reader(model, delimiter=';'))]

    def run(self):
        pg.init()
        # Местные переменные и константы:
        clock = pg.time.Clock()
        SECOND = pg.USEREVENT + 1
        background_color = pg.Color(31, 30, 38)

        # Задаём параметры окну:
        pg.display.set_caption('Отражение')
        self.screen = pg.display.set_mode(self.size)
        self.screen.fill(background_color)
        pg.time.set_timer(SECOND, 1000)

        # Основной цикл игры:
        while self.running:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.running = False
                if event.type == pg.MOUSEBUTTONDOWN:
                    for but in self.buttons:
                        if event.pos in but:
                            but.slot()
                if event.type == SECOND:
                    if not self.pause:
                        self.time += TimeDelta(seconds=1)
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_SPACE:
                        self.buttons[1].slot()  # Пауза
                    if event.key == pg.K_s and (event.mod & pg.KMOD_CTRL):
                        self.buttons[0].slot()  # Сохранить
                    if event.key == pg.K_HOME and (event.mod & pg.KMOD_CTRL):
                        self.buttons[2].slot()  # Выход

            # Отрисовка элементов:
            self.screen.fill(background_color)
            self.render()
            for el in self.buttons + self.displays:
                el.render()

            # Обновление элементов дисплеев:
            for i, el in enumerate((str(self.score), str(self.lifes),
                                    self.time.strftime('%M:%S'))):
                self.displays[i].set_item(el)

            clock.tick(self.FPS)
            pg.display.flip()
        pg.quit()

    def render(self):
        # Матрица блоков:
        x, y = self.blocks_left, self.blocks_top
        for i, row in enumerate(self.blocks):
            for j, el in enumerate(row):
                dr.rect(self.screen, pg.Color('white'),
                        (x, y, self.block_width, self.block_height),
                        width=2)  # Временно для проверки
                x += self.block_width
            y += self.block_height
            x = self.blocks_left

    def change_pause(self):
        self.pause = not self.pause

    def exit(self):
        self.running = False

    def save(self):
        print('Saved.')


class MainWindow:
    pass


if __name__ == '__main__':
    window = Game(None, 'DataBases/Level1_StartModel.csv')
    window.run()
