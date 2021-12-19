import pygame as pg
import pygame.draw as dr
import pygame.transform as tr
import pygame.sprite as spr
import csv
from datetime import datetime as DateTime
from datetime import timedelta as TimeDelta
import os


def load_image(name, color_key=None):
    fullname = os.path.join('Images', name)
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


def get_width(surface, height):
    return round(surface.get_size()[0] * (height / surface.get_size()[1]))


class Platform(spr.Sprite):
    def __init__(self, parent, group):
        super().__init__(group)
        self.parent = parent

        image = load_image("Platform.png", -1)
        self.h = 80
        self.w = get_width(image, self.h)
        self.image = tr.scale(image, (self.w, self.h))
        self.rect = self.image.get_rect()
        self.rect.x =  self.parent.w // 2 - self.w // 2
        self.rect.y = 650
        self.selected_delta_x = 0
        self.set_dict()
        self.edge = 30

        self.mask = pg.mask.from_surface(self.image)

    def update(self, delta_x):
        x = self.rect.x + delta_x - self.selected_delta_x
        if x < self.parent.border_w:
            x = self.parent.border_w
        if x > self.parent.w - self.w - self.parent.border_w:
             x = self.parent.w - self.w - self.parent.border_w
        delta_x = x - self.rect.x
        self.rect.x = x
        if self.parent.start:
            self.parent.triplex.update(delta_x=delta_x)

    def set_platform_size(self, size='middle'):
        name = {'short': "Short_platform.png", 'long': "Long_platform.png",
                'middle': "Platform.png"}.get(size, None)
        old_x = self.rect.x
        if name is None:
            print('Некорректный размер.')
            return
        image = load_image(name, -1)
        self.h = 80
        self.w = get_width(image, self.h)
        self.image = tr.scale(image, (self.w, self.h))
        self.rect = self.image.get_rect()
        self.rect.x = min(old_x, self.parent.w - self.rect.w)
        self.rect.y = 650
        self.set_dict()

    def set_select(self, select, pos=None):
        # Задание точки перетаскивания относительно левого края
        pos = (self.rect.x, self.rect.y) if pos is None else pos
        self.selected_delta_x = pos[0] - self.rect.x if select else 0

    def set_dict(self):
        self.angles_dict = {range(0, self.w // 10): (-7, -3),
                            range(self.w // 10, 2 * self.w // 10): (-5, -5),
                            range(2 * self.w // 10, 3 * self.w // 10): (-4, -6),
                            range(3 * self.w // 10, 4 * self.w // 10): (-3, -7),
                            range(4 * self.w // 10, 9 * self.w // 20): (-2, -8),
                            range(9 * self.w // 20, 11 * self.w // 20): (0, -9),
                            range(11 * self.w // 20, 6 * self.w // 10): (2, -8),
                            range(6 * self.w // 10, 7 * self.w // 10): (3, -7),
                            range(7 * self.w // 10, 8 * self.w // 10): (4, -6),
                            range(8 * self.w // 10, 9 * self.w // 10): (5, -5),
                            range(9 * self.w // 10, self.w): (7, -3)}

    def collide_triplex(self, point):
        x = point[0]
        for range_ in self.angles_dict.keys():
            if x in range_:
                self.parent.triplex.set_vx(self.angles_dict[range_][0])
                self.parent.triplex.set_vy(self.angles_dict[range_][1])


class Triplex(spr.Sprite):
    def __init__(self, parent, group):
        super().__init__(group)
        self.parent = parent

        self.h = self.w = 50
        self.image = tr.scale(load_image("Triplex2.png", -1), (self.w, self.h))
        self.rect = self.image.get_rect()
        self.rect.x = self.parent.w // 2 - self.w // 2
        self.rect.y = 602
        self.vx = self.vy = 0

        self.mask = pg.mask.from_surface(self.image)

    def update(self, delta_x=0):
        # Движение по платформе:
        if delta_x:
            x = self.rect.x + delta_x
            ed = self.parent.platform.edge
            condition = x >= self.parent.platform.rect.x + ed and\
                        x <= self.parent.platform.rect.x +\
                             self.parent.platform.rect.w - self.w - ed
            self.rect.x = x if condition else self.rect.x

        # Движение:
        self.rect.x += self.vx
        self.rect.y += self.vy
        if self.rect.y + self.h >= self.parent.death_y or\
                        self.rect.y < self.parent.blocks_top -\
                self.parent.border_w or\
                        self.rect.x <= 0 or\
                                self.rect.x + self.w >= self.parent.w:
            self.parent.die()

        # Отскоки от стенок:
        border = spr.spritecollideany(self, self.parent.borders)
        if border is not None:
            if border.location == 'ver':
                self.vx = -self.vx
            else:
                self.vy = -self.vy

        # Отскоки от платформы:
        point = spr.collide_mask(self.parent.platform, self)
        if point is not None and not self.parent.start:
            self.parent.platform.collide_triplex(point)

    def set_vx(self, vx):
        self.vx = vx

    def set_vy(self, vy):
        self.vy = vy


class Border(spr.Sprite):
    def __init__(self, parent, groups, x, y, w, h, degree):
        super().__init__(*groups)
        self.parent = parent
        self.h = h
        self.w = w
        self.image = tr.scale(tr.rotate(load_image("Border.png"), degree),
                              (self.w, self.h))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.location = 'hor' if self.w > self.h else 'ver'


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
            item_x = self.x + self.w - item.get_width() - self.w // 8
            im = tr.scale(load_image('Platform.png', -1), (5 * self.w // 8,
                                                           item.get_height()))
            screen.blit(im, (self.x + round(self.w // 8),
                        self.y + self.h - item.get_height() - 10))
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
        self.field_bottom = 730
        self.block_width = 90
        self.block_height = 50
        self.death_y = 690
        self.border_w = 20

        # Флаги:
        self.pause = False
        self.running = True
        self.start = True
        self.platform_selected = False

        # Создаём виджеты:
        self.buttons = [Button(self, 20, self.h - 60, 350, 50,
                               'Сохранить', slot=self.save),
                        Button(self, self.w // 2 - 175, self.h - 60, 350, 50,
                               'Пауза', slot=self.change_pause,
                               text2='Продолжить'),
                        Button(self, self.w - 370, self.h - 60, 350, 50,
                               'Выход', slot=self.exit)]
        self.displays = [TextDisplay(self, 20, 10, 300, 100,
                                     'Очки', str(self.score)),
                         TextDisplay(self, self.w // 2 - 150, 10, 300, 100,
                                     'Жизни', str(self.lifes), image=0),
                         TextDisplay(self, self.w - 320, 10, 300, 100,
                                     'Время', self.time.strftime('%M:%S'))]
        self.all_sprites = spr.Group()
        self.cursor_group = spr.Group()
        self.borders = spr.Group()

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
        im = load_image('Fone.png')
        fone = tr.scale(im, (get_width(im, self.h), self.h))
        self.screen.blit(fone, (0, 0))
        pg.time.set_timer(SECOND, 1000)
        pg.mouse.set_visible(False)
        pg.display.set_icon(load_image('Reflection_logo_2.png'))

        # Создаём спрайты:
        self.triplex = Triplex(self, self.all_sprites)
        self.platform = Platform(self, self.all_sprites)
        Border(self, (self.borders, self.all_sprites),
               self.blocks_left + len(self.blocks[0]) * self.block_width,
               self.blocks_top - self.border_w, self.border_w, 630, 90)
        Border(self, (self.borders, self.all_sprites),
               self.blocks_left - self.border_w,
               self.blocks_top - self.border_w, self.border_w, 630, 90)
        Border(self, (self.borders, self.all_sprites),
               self.blocks_left, self.blocks_top - self.border_w,
               len(self.blocks[0]) * self.block_width, self.border_w, 0)
        Border(self, (self.all_sprites, ),
               self.blocks_left, self.field_bottom,
               len(self.blocks[0]) * self.block_width, self.border_w, 0)
        self.cursor = spr.Sprite(self.cursor_group)
        self.cursor.image = load_image("cursor.png")
        self.cursor.rect = self.cursor.image.get_rect()

        # Основной цикл игры:
        while self.running:
            # Обработка событий:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.running = False
                if event.type == pg.MOUSEBUTTONDOWN:
                    for but in self.buttons:
                        if event.pos in but:
                            but.slot()
                    if self.platform.rect.collidepoint(event.pos) and\
                            not self.pause:
                        self.platform_selected = True
                        self.platform.set_select(True, event.pos)
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
                    if event.key == pg.K_UP:
                        print('start')
                        self.start = False
                if event.type == pg.MOUSEMOTION:
                    self.cursor.rect.topleft = event.pos
                    if self.platform_selected and not self.pause:
                        self.platform.update(event.pos[0] -\
                                             self.platform.rect.x)
                if event.type == pg.MOUSEBUTTONUP:
                    self.platform_selected = False
                    self.platform.set_select(False)
            if pg.key.get_pressed()[pg.K_LEFT] and not self.pause:
                if not pg.key.get_mods() & pg.KMOD_SHIFT:
                    self.platform.update(-10)
                else:
                    self.triplex.update(delta_x=-5)
            if pg.key.get_pressed()[pg.K_RIGHT] and not self.pause:
                if not pg.key.get_mods() & pg.KMOD_SHIFT:
                    self.platform.update(10)
                else:
                    self.triplex.update(delta_x=5)

            # Отрисовка элементов:
            self.screen.fill(background_color)
            self.screen.blit(fone, (0, 0))
            self.render()
            for el in self.buttons + self.displays:
                el.render()
            self.all_sprites.draw(self.screen)
            if pg.mouse.get_focused():
                self.cursor_group.draw(self.screen)

            # Движение:
            if not self.pause:
                self.triplex.update()

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
                x += self.block_width
            y += self.block_height
            x = self.blocks_left

    def change_pause(self):
        self.pause = not self.pause

    def exit(self):
        self.running = False

    def save(self):
        print('Saved.')

    def die(self):
        self.all_sprites.remove(self.triplex)
        self.all_sprites.remove(self.platform)
        if not self.start:
            self.lifes -= 1
        self.start = True
        if self.lifes <= 0:
            self.buttons[0].slot = do_nothing
            self.buttons[1].slot = do_nothing
            self.pause = True
        else:
            self.triplex = Triplex(self, self.all_sprites)
            self.platform = Platform(self, self.all_sprites)

    def no_blocks(self):
        return True


class MainWindow:
    pass


if __name__ == '__main__':
    window = Game(None, 'DataBases/Level1_StartModel.csv')
    window.run()
