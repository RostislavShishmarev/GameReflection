import pygame as pg
import pygame.draw as dr
import pygame.transform as tr
import pygame.sprite as spr
import pygame.mixer as mix
import csv
import os
from datetime import datetime as DateTime
from datetime import timedelta as TimeDelta
from random import choice


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


def do_nothing(*args, **kwargs):
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
        super().__init__(self.names, *groups, h=50)
        self.parent = parent
        self.groups = groups

        self.rect.x = self.parent.w // 2 - self.w // 2
        self.rect.y = self.parent.field_bottom - self.h
        self.selected_delta_x = 0
        self.set_dict()

        self.size_index = 1
        self.edge = 30
        self.crushing = False
        self.crushing_cadres = self.cur_cadres = round(1 / 3 * self.parent.FPS)
        self.selected = False

        self.mask = pg.mask.from_surface(self.image)

    def update(self):
        if self.crushing:
            self.cur_cadres -= 1
            if self.cur_cadres in [self.crushing_cadres // len(self.names) * i
                                   for i in range(1, len(self.names))]:
                self.update_image()
            if self.cur_cadres <= 0:
                self.cur_cadres = self.crushing_cadres
                self.parent.end_die()

    def move(self, delta_x):
        x = self.rect.x + delta_x - self.selected_delta_x
        if x < self.parent.border_w:
            x = self.parent.border_w
        if x > self.parent.w - self.w - self.parent.border_w:
            x = self.parent.w - self.w - self.parent.border_w
        delta_x = x - self.rect.x
        self.rect.x = x
        if self.parent.start:
            self.parent.triplex.move(delta_x)

    def change_platform_size(self, change=0):
        name_list = ["Short_platform.png", "Platform.png", "Long_platform.png"]
        index = self.size_index + change
        if index < 0 or index >= len(name_list):
            return
        self.size_index += change
        old_x, old_y = self.rect.x, self.rect.y
        self.names = [(name_list[self.size_index], -1)] + self.names[1:]
        self.make_frames(self.names, h=self.h)
        self.rect.x = min(old_x,
                          self.parent.w - self.rect.w - self.parent.border_w)
        self.rect.y = old_y
        self.mask = pg.mask.from_surface(self.image)
        self.set_dict()
        self.parent.platform_changed_sound.play()

    def set_select(self, select, pos=None):
        # Задание точки перетаскивания относительно левого края
        self.selected = select
        pos = (self.rect.x, self.rect.y) if pos is None else pos
        self.selected_delta_x = pos[0] - self.rect.x if select else 0

    def set_dict(self, coef=5):
        self.angles_dict = {}
        fps = self.parent.FPS
        vx, vy = coef * -100 / fps, coef * -10 / fps
        step = coef * 10 / fps
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
        from_start = self.parent.triplex.vx == self.parent.triplex.vy == 0
        for range_ in self.angles_dict.keys():
            if x in range_:
                self.parent.triplex.set_vx(self.angles_dict[range_][0])
                self.parent.triplex.set_vy(self.angles_dict[range_][1])
                if not from_start:
                    self.parent.collide_sound.play()
                break

    def process_move(self):
        if not pg.key.get_mods() & pg.KMOD_SHIFT:
            if pg.key.get_pressed()[pg.K_RIGHT] and not self.parent.pause:
                self.move(10)
            if pg.key.get_pressed()[pg.K_LEFT] and not self.parent.pause:
                self.move(-10)

    def process_event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos) and not self.parent.pause:
                self.set_select(True, event.pos)
        if event.type == pg.MOUSEMOTION:
            if self.selected and not self.parent.pause:
                self.move(event.pos[0] - self.rect.x)
        if event.type == pg.MOUSEBUTTONUP:
            self.set_select(False)


class Triplex(spr.Sprite):
    def __init__(self, parent, group):
        super().__init__(group)
        self.parent = parent

        self.h = self.w = 35
        self.image = tr.scale(load_image("Triplex.png", -1), (self.w, self.h))
        self.rect = self.image.get_rect()
        self.rect.x = self.parent.w // 2 - self.w // 2
        self.rect.y = self.parent.field_bottom -\
                      self.parent.platform.h - self.h + 2
        self.vx = self.vy = 0

        self.mask = pg.mask.from_surface(self.image)
        self.died = False

    def update(self):
        # Движение:
        old_x, old_y = self.rect.x, self.rect.y
        self.rect.x += self.vx
        self.rect.y += self.vy
        if self.rect.y + self.h >= self.parent.death_y and not self.died:
            self.died = True
            self.parent.begin_die()
            return

        # Отскоки от стенок:
        border = spr.spritecollideany(self, self.parent.borders)
        if border is not None:
            border.collide_triplex()

        # Отскоки от платформы:
        point = spr.collide_mask(self.parent.platform, self)
        if point is not None and not self.parent.start:
            self.parent.platform.collide_triplex(point)

        # Отскоки от блоков:
        blocks = spr.spritecollide(self, self.parent.blocks_group, False)
        for block in blocks:
            if block is not None:
                point = spr.collide_mask(block, self)
                if point is not None:
                    block.collide_triplex(point)

        # Защита от выталкивания за пределы поля:
        if self.rect.y < self.parent.blocks_top:
            self.rect.y = old_y + 1
        if self.rect.x < self.parent.border_w:
            self.rect.x = old_x + 1
        if self.rect.x + self.w > self.parent.w - self.parent.border_w:
            self.rect.x = old_x - 1

        # Защита от горизонтальных отскоков:
        if self.vy == 0 and self.vx != 0:
            self.vy += 2
            print('Исправлено.')

    def move(self, delta_x):
        x = self.rect.x + delta_x
        ed = self.parent.platform.edge
        min_x = self.parent.platform.rect.x
        min_x += self.parent.platform.rect.w - self.w - ed
        self.rect.x = x if self.parent.platform.rect.x + ed <= x <= min_x\
            else self.rect.x

    def set_vx(self, vx):
        self.vx = vx

    def set_vy(self, vy):
        self.vy = vy

    def change_v(self, coef):
        self.vx *= coef
        self.vy *= coef

    def process_move(self):
        if pg.key.get_mods() & pg.KMOD_SHIFT and not self.parent.pause:
            if pg.key.get_pressed()[pg.K_LEFT]:
                self.move(-5)
            if pg.key.get_pressed()[pg.K_RIGHT]:
                self.move(5)


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

    def collide_triplex(self):
        if self.location == 'ver':
            self.parent.triplex.vx = -self.parent.triplex.vx
        else:
            self.parent.triplex.vy = -self.parent.triplex.vy
        self.parent.collide_sound.play()


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
                                        [self.parent.all_sprites,
                                         self.ver_bord_group]),
                        BlockBorder(self, x + self.w - 1, y, 1, self.h,
                                        [self.parent.all_sprites,
                                         self.ver_bord_group]),
                        BlockBorder(self, x + 1, y, self.w - 2, 1,
                                        [self.parent.all_sprites,
                                         self.hor_bord_group]),
                        BlockBorder(self, x + 1, y + self.h - 1, self.w - 2, 1,
                                        [self.parent.all_sprites,
                                         self.hor_bord_group])]

        self.mask = pg.mask.from_surface(self.image)
        self.crush_score = 100
        classes = [None] * 24 + [Treasure] * 16 + [HealthTreasure] +\
            [LongMakerTreasure] * 4 + [ShortMakerTreasure] * 4
        self.treasure_class = choice(classes)
        self.collide_sound = self.parent.collide_sound

    def crush(self):
        self.parent.all_sprites.remove(self)
        self.parent.blocks_group.remove(self)
        self.parent.blocks[self.i][self.j] = None
        for bord in self.borders:
            self.parent.all_sprites.remove(bord)
        self.parent.score += self.crush_score
        if self.treasure_class is not None:
            self.treasure_class(self.parent, self.rect.x, self.rect.y,
                                self.parent.all_sprites,
                                self.parent.treasures_group)

    def collide_triplex(self, point):
        self.crush_self = False
        old_x, old_y = point
        old_vx, old_vy = self.parent.triplex.vx, self.parent.triplex.vy
        ver_bord = spr.spritecollideany(self.parent.triplex,
                                        self.ver_bord_group)
        if ver_bord and spr.collide_mask(self.parent.triplex, ver_bord)\
                and ((old_x < self.w / 2 and old_vx >= 0) or
                         (old_x > self.w / 2 and old_vx <= 0)):
            self.parent.triplex.set_vx(-old_vx)
            self.crush_self = True
        hor_bord = spr.spritecollideany(self.parent.triplex,
                                        self.hor_bord_group)
        if hor_bord and spr.collide_mask(self.parent.triplex, hor_bord)\
                and ((old_y < self.h / 2 and old_vy >= 0) or
                         (old_y > self.h / 2 and old_vy <= 0)):
            self.parent.triplex.set_vy(-old_vy)
            self.crush_self = True
        if self.crush_self:
            self.crush()
            self.collide_sound.play()
        if not self.crush_self and not isinstance(self, ScBlock):
            self.parent.triplex.set_vx(-old_vx)
            self.parent.triplex.set_vy(-old_vy)
            self.crush()
            self.collide_sound.play()


class ScBlock(Block):
    def __init__(self, parent, x, y, w, h, i, j, *groups):
        super().__init__(parent, x, y, w, h, i, j, *groups)
        self.image = tr.scale(load_image('Sc_block.png'), (self.w, self.h))
        self.before_crushing = 30
        self.treasure_class = None
        self.crush_score = 400

    def crush(self):
        self.before_crushing -= 1
        if self.before_crushing <= 0:
            super().crush()


class BrickedBlock(Block):
    def __init__(self, parent, x, y, w, h, i, j, *groups):
        super().__init__(parent, x, y, w, h, i, j, *groups)
        self.image = tr.scale(load_image('Bricked_block.png'),
                              (self.w, self.h))
        self.before_crushing = 2
        self.crush_score = 200

    def crush(self):
        self.before_crushing -= 1
        if self.before_crushing == 1:
            self.image = tr.scale(load_image('Bricked_block_crushing.png'),
                              (self.w, self.h))
            self.parent.score += 50
        if self.before_crushing <= 0:
            super().crush()


class DeathBlock(Block):
    def __init__(self, parent, x, y, w, h, i, j, *groups):
        super().__init__(parent, x, y, w, h, i, j, *groups)
        self.image = tr.scale(load_image('Death_block.png'),
                              (self.w, self.h))
        self.crush_score = 600
        self.treasure_class = DeathTreasure
        self.collide_sound = self.parent.death_collide_sound


class ExplodingBlock(Block):
    def __init__(self, parent, x, y, w, h, i, j, *groups):
        super().__init__(parent, x, y, w, h, i, j, *groups)
        self.image = tr.scale(load_image('Exploding_block.png'),
                              (self.w, self.h))
        self.cur_index = 0
        self.frames = [self.image] + self.cut_frames(
            'Exploding_block_crushing_sprites.png', 6, 8)
        self.crush_score = 50
        self.crushing = False
        self.collide_sound = self.parent.crush_sound

    def crush(self, only_self=False):
        if not only_self:
            for coords in self.get_neighbourhood_coords():
                i, j = coords
                if not isinstance(self.parent.blocks[i][j], DeathBlock):
                    self.parent.blocks[i][j].treasure_class =\
                        self.treasure_class
                if isinstance(self.parent.blocks[i][j],
                              ExplodingBlock):
                    self.parent.blocks[i][j].crush(only_self=True)
                else:
                    self.parent.blocks[i][j].crush()
        for bord in self.borders:
            self.parent.all_sprites.remove(bord)
        self.parent.score += self.crush_score
        self.collide_triplex = do_nothing
        self.crushing = True
        if self.treasure_class is not None:
            self.treasure_class(self.parent, self.rect.x, self.rect.y,
                                self.parent.all_sprites,
                                self.parent.treasures_group)

    def update(self):
        if self.crushing:
            self.cur_index += 1
            self.image = self.frames[self.cur_index]
            if self.cur_index >= len(self.frames) - 1:
                self.end_crush()

    def end_crush(self):
        self.parent.all_sprites.remove(self)
        self.parent.blocks_group.remove(self)
        self.parent.blocks[self.i][self.j] = None

    def get_neighbourhood_coords(self):
        blocks, i, j = self.parent.blocks, self.i, self.j
        coords = []
        for i, j in [[i + 1, j + 1], [i + 1, j], [i, j + 1], [i - 1, j - 1],
                     [i - 1, j], [i, j - 1], [i + 1, j - 1], [i - 1, j + 1]]:
            if 0 <= i < len(blocks) and 0 <= j < len(blocks[0])\
                    and blocks[i][j] is not None:
                coords.append((i, j))
        return coords

    def cut_frames(self, im_name, rows, columns):
        sheet = load_image(im_name)
        rect = pg.Rect(0, 0, sheet.get_width() // columns,
                       sheet.get_height() // rows)
        frames = []
        for j in range(rows):
            for i in range(columns):
                frame_location = (rect.w * i, rect.h * j)
                frames.append(tr.scale(sheet.subsurface(pg.Rect(
                    frame_location, rect.size)), (self.w, self.h)))
        return frames


class BlockBorder(spr.Sprite):
    def __init__(self, parent, x, y, w, h, *groups):
        super().__init__(*groups)
        self.parent = parent
        self.w, self.h = w, h
        self.image = tr.scale(load_image('Block_border.png'), (self.w, self.h))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

        self.mask = pg.mask.from_surface(self.image)


class Treasure(spr.Sprite):
    def __init__(self, parent, x, y, *groups):
        super().__init__(*groups)
        self.parent = parent
        self.image = tr.scale(load_image('Treasure.png', -1),
                              (self.parent.block_width,
                               self.parent.block_height))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.v = 300 / self.parent.FPS

        self.mask = pg.mask.from_surface(self.image)

    def update(self):
        self.rect.y += self.v
        if self.rect.y + self.rect.h >= self.parent.death_y:
            self.delete()
        if spr.collide_mask(self, self.parent.platform):
            self.effect()
            self.delete()

    def delete(self):
        self.parent.all_sprites.remove(self)
        self.parent.treasures_group.remove(self)

    def effect(self):
        self.parent.score += 120
        self.parent.treasure_sound.play()


class DeathTreasure(Treasure):
    def __init__(self, parent, x, y, *groups):
        super().__init__(parent, x, y, *groups)
        self.image = tr.scale(load_image('Death_block.png'),
                              (self.parent.block_width,
                               self.parent.block_height))
        self.mask = pg.mask.from_surface(self.image)
        self.v = 400 / self.parent.FPS

    def effect(self):
        self.parent.begin_die()


class HealthTreasure(Treasure):
    def __init__(self, parent, x, y, *groups):
        super().__init__(parent, x, y, *groups)
        self.image = tr.scale(load_image('Health_treasure.png', -1),
                              (self.parent.block_width,
                               self.parent.block_height))
        self.mask = pg.mask.from_surface(self.image)

    def effect(self):
        self.parent.lifes += 1
        self.parent.life_added_sound.play()


class LongMakerTreasure(Treasure):
    def __init__(self, parent, x, y, *groups):
        super().__init__(parent, x, y, *groups)
        self.image = tr.scale(load_image('Long_maker.png', -1),
                              (self.parent.block_width,
                               self.parent.block_height))
        self.mask = pg.mask.from_surface(self.image)

    def effect(self):
        self.parent.platform.change_platform_size(1)


class ShortMakerTreasure(Treasure):
    def __init__(self, parent, x, y, *groups):
        super().__init__(parent, x, y, *groups)
        self.image = tr.scale(load_image('Short_maker.png', -1),
                              (self.parent.block_width,
                               self.parent.block_height))
        self.mask = pg.mask.from_surface(self.image)
        self.sound = self.parent.platform_changed_sound

    def effect(self):
        self.parent.platform.change_platform_size(-1)


class Button:
    def __init__(self, parent, x, y, w, h, text, font_size=40,
                 main_color=pg.Color(70, 202, 232),
                 back_color=pg.Color(0, 0, 0), slot=do_nothing, text2=None,
                 key=None, modifier=None):
        self.parent = parent
        self.x, self.y, self.x1, self.y1 = x, y, x + w, y + h
        self.w, self.h = w, h
        self.function = slot

        self.text = text
        self.text2 = text2 if text2 is not None else text
        self.current_text = self.text
        self.font_size = font_size

        self.main_color = main_color
        self.light_main_color = pg.Color(min(self.main_color.r + 90, 255),
                                         min(self.main_color.g + 90, 255),
                                         min(self.main_color.b + 90, 255))
        self.current_color = self.main_color
        self.back_color = back_color

        self.key = key
        self.modifier = modifier

    def slot(self):
        # Декорация переданной функции:
        self.current_text = self.text if self.current_text == self.text2\
            else self.text2

        self.function()

    def render(self):
        screen = self.parent.screen
        dr.rect(screen, self.back_color,
                (self.x, self.y, self.w, self.h))
        dr.rect(screen, self.current_color,
                (self.x, self.y, self.w, self.h), width=2)
        font = pg.font.Font(None, self.font_size)
        text = font.render(self.current_text, True, self.current_color)
        screen.blit(text, (self.x + self.w // 2 - text.get_width() // 2,
                           self.y + self.h // 2 - text.get_height() // 2))

    def __contains__(self, item):
        return item[0] in range(self.x, self.x1) and\
               item[1] in range(self.y, self.y1)

    def process_event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN:
            if event.pos in self:
                self.slot()
        if event.type == pg.KEYDOWN and self.key is not None:
            if event.key == self.key:
                if self.modifier is not None:
                    if event.mod & self.modifier:
                        self.slot()
                else:
                    self.slot()
        if event.type == pg.MOUSEMOTION:
            if event.pos in self:
                self.current_color = self.light_main_color
            else:
                self.current_color = self.main_color


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
        self.blocks_dict = {'nothing': None, 'Block.png': Block,
                            'Sc_block.png': ScBlock,
                            'Bricked_block.png': BrickedBlock,
                            'Death_block.png': DeathBlock,
                            'Exploding_block.png': ExplodingBlock}
        self.block_code_dict = {None: 'nothing', Block: 'Block.png'}

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
        self.game_ended = False

        # Создаём виджеты:
        self.buttons = [Button(self, 20, self.h - 60, 350, 50,
                               'Сохранить', slot=self.save,
                               key=pg.K_s, modifier=pg.KMOD_CTRL),
                        Button(self, self.w // 2 - 175, self.h - 60, 350, 50,
                               'Пауза', slot=self.change_pause,
                               text2='Продолжить', key=pg.K_SPACE),
                        Button(self, self.w - 370, self.h - 60, 350, 50,
                               'Выход', slot=self.exit,
                               key=pg.K_HOME, modifier=pg.KMOD_CTRL)]
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
        self.treasures_group = spr.Group()

        # Открываем модель расположения блоков:
        with open(self.mod_name, encoding='utf8') as model:
            self.blocks_model = list(csv.reader(model, delimiter=';'))

    def run(self):
        pg.init()
        mix.init()
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

        # Создаём звуки:
        self.collide_sound = mix.Sound('Sounds/collide.mp3')
        self.win_sound = mix.Sound('Sounds/win.mp3')
        self.game_over_sound = mix.Sound('Sounds/game_over.mp3')
        self.crush_sound = mix.Sound('Sounds/crush.mp3')
        self.death_collide_sound = mix.Sound('Sounds/death_collide.mp3')
        self.life_added_sound = mix.Sound('Sounds/life_added.mp3')
        self.platform_changed_sound = mix.Sound('Sounds/platform_changed.mp3')
        self.treasure_sound = mix.Sound('Sounds/treasure_on_platform.mp3')
        self.platform_crushed_sound = mix.Sound('Sounds/platform_crushing.mp3')

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
                for but in self.buttons:
                    but.process_event(event)
                self.platform.process_event(event)
                if event.type == pg.QUIT:
                    self.running = False
                if event.type == SECOND and not self.start:
                    if not self.pause:
                        self.time += TimeDelta(seconds=1)
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_UP:
                        self.start = False
                if event.type == pg.MOUSEBUTTONDOWN:
                    if event.button == 2:
                        self.start = False
                if event.type == pg.MOUSEMOTION:
                    self.cursor.rect.topleft = event.pos
            self.platform.process_move()
            if self.start:
                self.triplex.process_move()

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

            # Обновление элементов:
            for i, el in enumerate((str(self.score), str(self.lifes),
                                    self.time.strftime('%M:%S'))):
                self.displays[i].set_item(el)
            if not self.pause:
                self.blocks_group.update()
                self.treasures_group.update()
            clock.tick(self.FPS)
            pg.display.flip()

            # Проверка на выигрыш:
            if self.no_blocks() and not self.game_ended:
                self.win()
        pg.quit()
        mix.quit()
        if self.new_window_after_self is not None:
            self.new_window_after_self.run()

    def make_blocks(self, model):
        matrix = []
        x, y = self.blocks_left, self.blocks_top
        for i, row in enumerate(model):
            lst = []
            for j, el in enumerate(row):
                block_class = self.blocks_dict[el]
                if block_class is not None:
                    block = block_class(self, x, y, self.block_width,
                                        self.block_height, i, j,
                                        self.all_sprites, self.blocks_group)
                else:
                    block = None
                x += self.block_width
                lst.append(block)
            y += self.block_height
            x = self.blocks_left
            matrix.append(lst)
        return matrix

    def change_pause(self):
        self.pause = not self.pause
        if self.pause:
            mix.pause()
        else:
            mix.unpause()

    def exit(self):
        self.running = False

    def save(self):
        print('Saved.')

    def begin_die(self):
        self.all_sprites.remove(self.triplex)
        self.platform.crushing = True
        self.platform_crushed_sound.play()

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
            self.game_over_sound.play()
            self.game_ended = True
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
        self.win_sound.play()
        self.game_ended = True

    def restart(self):
        self.exit()
        self.new_window_after_self = Game(self.parent,
                                          self.mod_name.split('_')[0] +\
                                          '_StartModel.csv')

    def no_blocks(self):
        return all([b is None or isinstance(b, ScBlock)
                    for row in self.blocks for b in row])


class MainWindow:
    pass


if __name__ == '__main__':
    window = Game(None, 'DataBases/Level9_StartModel.csv')
    window.run()
