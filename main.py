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


class AnimatedSprite(spr.Sprite):
    def __init__(self, names, *groups, h=None):
        super().__init__(*groups)
        self.make_frames(names, h)

    def make_frames(self, names, h=None):
        self.frames = list(map(lambda x: load_image(*x), names))
        self.cur_index = 0
        if h is not None:
            self.h = h
            self.w = get_width(self.frames[self.cur_index], self.h)
            self.frames = list(map(lambda x: tr.scale(x, (self.w, self.h)),
                                   self.frames))
        self.image = self.frames[self.cur_index]
        self.rect = self.image.get_rect()

    def update_image(self):
        self.cur_index = (self.cur_index + 1) % len(self.frames)
        self.image = self.frames[self.cur_index]


class Platform(AnimatedSprite):
    def __init__(self, parent, *groups):
        self.names = [("Platform.png", -1), ("Platform_crushing_1.png", -1),
                      ("Platform_crushing_2.png", -1)]
        super().__init__(self.names, *groups, h=60)
        self.parent = parent
        self.groups = groups

        self.rect.x = self.parent.w // 2 - self.w // 2
        self.rect.y = self.parent.field_bottom - self.h
        self.selected_delta_x = 0
        self.set_dict()

        self.edge = 30
        self.crushing = False
        self.crushing_cadres = self.cur_cadres = round(1 / 3 * self.parent.FPS)

        self.mask = pg.mask.from_surface(self.image)

    def update(self, delta_x=0):
        if delta_x:
            x = self.rect.x + delta_x - self.selected_delta_x
            if x < self.parent.border_w:
                x = self.parent.border_w
            if x > self.parent.w - self.w - self.parent.border_w:
                x = self.parent.w - self.w - self.parent.border_w
            delta_x = x - self.rect.x
            self.rect.x = x
            if self.parent.start:
                self.parent.triplex.update(delta_x=delta_x)
        if self.crushing:
            self.cur_cadres -= 1
            if self.cur_cadres in [self.crushing_cadres // len(self.names) * i
                                   for i in range(1, len(self.names))]:
                self.update_image()
            if self.cur_cadres <= 0:
                self.cur_cadres = self.crushing_cadres
                self.parent.end_die()

    def set_platform_size(self, size='middle'):
        name = {'short': "Short_platform.png", 'long': "Long_platform.png",
                'middle': "Platform.png"}.get(size, None)
        if name is None:
            print('Некорректный размер.')
            return
        old_x, old_y = self.rect.x, self.rect.y
        self.names = [(name, -1)] + self.names[1:]
        self.make_frames(self.names, h=self.h)
        self.rect.x = old_x
        self.rect.y = old_y
        self.mask = pg.mask.from_surface(self.image)
        self.set_dict()

    def set_select(self, select, pos=None):
        # Задание точки перетаскивания относительно левого края
        pos = (self.rect.x, self.rect.y) if pos is None else pos
        self.selected_delta_x = pos[0] - self.rect.x if select else 0

    def set_dict(self):
        self.angles_dict = {}
        fps = self.parent.FPS
        vx, vy = -400 / fps, -40 / fps
        step = 40 / fps
        for i in range(0, 9):
            self.angles_dict[range(self.w // 20 * i,
                                   self.w // 20 * (i + 1))] = (vx, vy)
            vx += step
            vy -= step
        self.angles_dict[range(self.w // 20 * 9,
                               self.w // 40 * 19)] = (vx, vy)
        vx += step
        vy -= step
        self.angles_dict[range(self.w // 40 * 19,
                               self.w // 40 * 21)] = (vx, vy)
        vx += step
        vy += step
        self.angles_dict[range(self.w // 40 * 21,
                               self.w // 20 * 11)] = (vx, vy)
        for i in range(11, 20):
            vx += step
            vy += step
            self.angles_dict[range(self.w // 20 * i,
                                   self.w // 20 * (i + 1))] = (vx, vy)

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

        self.h = self.w = 40
        self.image = tr.scale(load_image("Triplex.png", -1), (self.w, self.h))
        self.rect = self.image.get_rect()
        self.rect.x = self.parent.w // 2 - self.w // 2
        self.rect.y = self.parent.field_bottom -\
                      self.parent.platform.h - self.h + 2
        self.vx = self.vy = 0

        self.mask = pg.mask.from_surface(self.image)

    def update(self, delta_x=0):
        # Движение по платформе:
        if delta_x:
            x = self.rect.x + delta_x
            ed = self.parent.platform.edge
            min_x = self.parent.platform.rect.x
            min_x += self.parent.platform.rect.w - self.w - ed
            self.rect.x = x if self.parent.platform.rect.x + ed <= x <= min_x\
                else self.rect.x

        # Движение:
        old_x, old_y = self.rect.x, self.rect.y
        self.rect.x += self.vx
        self.rect.y += self.vy
        if self.rect.y + self.h >= self.parent.death_y:
            self.parent.begin_die()
            return

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

        # Отскоки от блоков:
        block = spr.spritecollideany(self, self.parent.blocks_group)
        if block is not None:
            point = spr.collide_mask(block, self)
            if point is not None:
                block.collide_triplex(point)
                block.crush()

        # Защита от выталкивания за пределы поля:
        if self.rect.y < self.parent.blocks_top:
            self.rect.y = old_y - 1
        if self.rect.x < self.parent.border_w:
            self.rect.x = old_x + 1
        if self.rect.x + self.w > self.parent.w - self.parent.border_w:
            self.rect.x = old_x - 1

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


class Block(spr.Sprite):
    def __init__(self, parent, x, y, w, h, i, j, *groups):
        super().__init__(*groups)
        self.parent = parent
        self.w, self.h, self.i, self.j = w, h, i, j
        self.image = tr.scale(load_image('Block.png'), (self.w, self.h))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

        self.ver_bord_group = spr.Group()
        self.hor_bord_group = spr.Group()
        self.borders = [BlockBorder(self, x, y, 1, self.h,
                                        *list(groups) + [self.ver_bord_group]),
                        BlockBorder(self, x + self.w - 1, y, 1, self.h,
                                        *list(groups) + [self.ver_bord_group]),
                        BlockBorder(self, x + 1, y, self.w - 2, 1,
                                        *list(groups) + [self.hor_bord_group]),
                        BlockBorder(self, x + 1, y + self.h - 1, self.w - 2, 1,
                                        *list(groups) + [self.hor_bord_group])]

        self.mask = pg.mask.from_surface(self.image)

    def crush(self):
        self.parent.all_sprites.remove(self)
        self.parent.blocks_group.remove(self)
        self.parent.blocks[self.i][self.j] = None
        for bord in self.borders:
            self.parent.all_sprites.remove(bord)
            self.parent.blocks_group.remove(bord)
        self.parent.score += 100

    def collide_triplex(self, point):
        old_x, old_y = point
        old_vx, old_vy = self.parent.triplex.vx, self.parent.triplex.vy
        ver_bord = spr.spritecollideany(self.parent.triplex,
                                        self.ver_bord_group)
        if ver_bord and spr.collide_mask(self.parent.triplex, ver_bord)\
                and ((old_x < self.w / 2 and old_vx >= 0) or
                         (old_x > self.w / 2 and old_vx <= 0)):
            self.parent.triplex.set_vx(-old_vx)
        hor_bord = spr.spritecollideany(self.parent.triplex,
                                        self.hor_bord_group)
        if hor_bord and spr.collide_mask(self.parent.triplex, hor_bord)\
                and ((old_y < self.h / 2 and old_vy >= 0) or
                         (old_y > self.h / 2 and old_vy <= 0)):
            self.parent.triplex.set_vy(-old_vy)


class BlockBorder(spr.Sprite):
    def __init__(self, parent, x, y, w, h, *groups):
        super().__init__(*groups)
        self.parent = parent
        self.w, self.h = w, h
        self.image = tr.scale(load_image('Block_border.png'), (self.w, self.h))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

        self.mask = pg.mask.from_surface(self.image)


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
        self.blocks_dict = {'nothing': None, 'block': Block}
        self.block_code_dict = {None: 'nothing', Block: 'block'}

        self.parent = parent
        self.mod_name = csv_model_name
        self.score = score
        self.time = DateTime(2020, 1, 1, 1, *time)
        self.lifes = lifes

        self.FPS = 80
        self.size = (self.w, self.h) = (1210, 820)
        self.blocks_left = 20
        self.blocks_top = 140
        self.field_bottom = 730
        self.block_width = 90
        self.block_height = 50
        self.death_y = 710
        self.border_w = 20

        # Флаги:
        self.pause = False
        self.running = True
        self.start = True
        self.platform_selected = False
        self.new_window_after_self = None

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
        self.blocks_group = spr.Group()

        # Открываем модель расположения блоков:
        with open(self.mod_name, encoding='utf8') as model:
            self.blocks_model = list(csv.reader(model, delimiter=';'))

    def run(self):
        pg.init()
        # Местные переменные и константы:
        clock = pg.time.Clock()
        SECOND = pg.USEREVENT + 1

        # Задаём параметры окну:
        pg.display.set_caption('Отражение')
        self.screen = pg.display.set_mode(self.size)
        im = load_image('Fone.png')
        fone = tr.scale(im, (get_width(im, self.h), self.h))
        self.screen.blit(fone, (0, 0))
        pg.time.set_timer(SECOND, 1000)
        pg.mouse.set_visible(False)
        pg.display.set_icon(load_image('Reflection_logo.png'))

        # Создаём спрайты:
        self.platform = Platform(self, self.all_sprites)
        self.triplex = Triplex(self, self.all_sprites)
        self.blocks = self.make_blocks(self.blocks_model)
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
                        print('Start!')
                        self.start = False
                if event.type == pg.MOUSEMOTION:
                    self.cursor.rect.topleft = event.pos
                    if self.platform_selected and not self.pause:
                        self.platform.update(event.pos[0] -
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
            self.screen.blit(fone, (0, 0))
            for el in self.buttons + self.displays:
                el.render()
            self.all_sprites.draw(self.screen)
            if pg.mouse.get_focused():
                self.cursor_group.draw(self.screen)

            # Движение:
            if not self.pause:
                self.triplex.update()
                self.platform.update()

            # Обновление элементов дисплеев:
            for i, el in enumerate((str(self.score), str(self.lifes),
                                    self.time.strftime('%M:%S'))):
                self.displays[i].set_item(el)

            clock.tick(self.FPS)
            pg.display.flip()
            if self.no_blocks():
                self.win()
        pg.quit()
        if self.new_window_after_self is not None:
            self.new_window_after_self.run()

    def make_blocks(self, model):
        matrix = []
        x, y = self.blocks_left, self.blocks_top
        for i, row in enumerate(model):
            lst = []
            for j, el in enumerate(row):
                x += self.block_width
                block_class = self.blocks_dict[el]
                if block_class is not None:
                    block = block_class(self, x, y, self.block_width,
                                        self.block_height, i, j,
                                        self.all_sprites, self.blocks_group)
                else:
                    block = None
                lst.append(block)
            y += self.block_height
            x = self.blocks_left
            matrix.append(lst)
        return matrix

    def change_pause(self):
        self.pause = not self.pause

    def exit(self):
        self.running = False

    def save(self):
        print('Saved.')

    def begin_die(self):
        self.all_sprites.remove(self.triplex)
        self.platform.crushing = True

    def end_die(self):
        self.all_sprites.remove(self.platform)
        if not self.start:
            self.lifes -= 1
        self.start = True
        if self.lifes <= 0:
            self.buttons[0].function = self.restart
            self.buttons[0].text = self.buttons[0].current_text = 'Начать \
сначала'
            self.buttons[1].slot = do_nothing
            self.pause = True
            g_over = spr.Sprite(self.all_sprites)
            g_over.image = load_image('Game_over.png', -1)
            g_over.rect = g_over.image.get_rect()
            g_over.rect.topleft = (self.w // 2 - g_over.rect[2] // 2,
                                   self.h // 2 - g_over.rect[3] // 2)
        else:
            self.platform = Platform(self, self.all_sprites)
            self.triplex = Triplex(self, self.all_sprites)

    def win(self):
        self.buttons[0].function = self.restart
        self.buttons[0].text = self.buttons[0].current_text = 'Начать \
сначала'
        self.buttons[1].slot = do_nothing
        self.pause = True
        you_win = spr.Sprite(self.all_sprites)
        you_win.image = load_image('You_win.png', -1)
        you_win.rect = you_win.image.get_rect()
        you_win.rect.topleft = (self.w // 2 - you_win.rect[2] // 2,
                                self.h // 2 - you_win.rect[3] // 2)

    def restart(self):
        self.exit()
        self.new_window_after_self = Game(self.parent,
                                          self.mod_name.split('_')[0] +\
                                          '_StartModel.csv')

    def no_blocks(self):
        return all([b is None for row in self.blocks for b in row])


class MainWindow:
    pass


if __name__ == '__main__':
    window = Game(None, 'DataBases/Level2_StartModel.csv')
    window.run()
