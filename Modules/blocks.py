from random import choice

import pygame as pg
import pygame.sprite as spr
import pygame.transform as tr
from Modules.treasures import Treasure, HealthTreasure, DeathTreasure,\
    LongMakerTreasure, ShortMakerTreasure

from Modules.helpers import load_image, do_nothing


class Block(spr.Sprite):
    def __init__(self, parent, x, y, w, h, i, j, *groups):
        super().__init__(*groups)
        self.parent = parent
        self.groups = groups
        self.w, self.h, self.i, self.j = w, h, i, j
        self.image = tr.scale(load_image('Block.png'), (self.w, self.h))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

        self.ver_bord_group = spr.Group()
        self.hor_bord_group = spr.Group()
        self.borders = [BlockBorder(self, x, y, 1, self.h, Place.LEFT,
                                    self.parent.all_sprites,
                                    self.ver_bord_group),
                        BlockBorder(self, x + self.w - 1, y, 1, self.h,
                                    Place.RIGHT,
                                    self.parent.all_sprites,
                                    self.ver_bord_group),
                        BlockBorder(self, x + 1, y, self.w - 2, 1, Place.TOP,
                                    self.parent.all_sprites,
                                    self.hor_bord_group),
                        BlockBorder(self, x + 1, y + self.h - 1, self.w - 2, 1,
                                    Place.BOTTOM,
                                    self.parent.all_sprites,
                                    self.hor_bord_group)]

        self.crush_self = False
        self.crushing = False

        self.mask = pg.mask.from_surface(self.image)
        self.crush_score = 100
        classes = [None] * 48 + [Treasure] * 32 + [HealthTreasure] +\
            [LongMakerTreasure] * 8 + [ShortMakerTreasure] * 8
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
                                self.parent.temporary_group)

    def collide_triplex(self):
        self.crush_self = False
        old_vx, old_vy = self.parent.triplex.vx, self.parent.triplex.vy
        ver_bord = spr.spritecollideany(self.parent.triplex,
                                        self.ver_bord_group)
        if ver_bord and spr.collide_mask(self.parent.triplex, ver_bord)\
                and ((ver_bord.place == Place.LEFT and old_vx >= 0) or
                     (ver_bord.place == Place.RIGHT and old_vx <= 0)):
            self.parent.triplex.set_vx(-old_vx)
            self.crush_self = True
        hor_bord = spr.spritecollideany(self.parent.triplex,
                                        self.hor_bord_group)
        if hor_bord and spr.collide_mask(self.parent.triplex, hor_bord)\
                and ((hor_bord.place == Place.TOP and old_vy >= 0) or
                     (hor_bord.place == Place.BOTTOM and old_vy <= 0)):
            self.parent.triplex.set_vy(-old_vy)
            self.crush_self = True
        if self.crush_self:
            self.crush()
            self.collide_sound.play()


class Place:
    TOP = 'top'
    BOTTOM = 'bottom'
    LEFT = 'left'
    RIGHT = 'right'


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
            self.treasure_class = None
            super().crush()


class BrickedBlock(Block):
    def __init__(self, parent, x, y, w, h, i, j, *groups):
        super().__init__(parent, x, y, w, h, i, j, *groups)
        self.image = tr.scale(load_image('Bricked_block.png'),
                              (self.w, self.h))
        self.treasure_class = None
        self.crush_score = 50

    def crush(self):
        tr_class, self.treasure_class = self.treasure_class, None
        super().crush()
        block = CrushedBrickedBlock(self.parent, self.rect.x, self.rect.y,
                                    self.w, self.h, self.i, self.j,
                                    *self.groups)
        self.parent.blocks[self.i][self.j] = block
        self.parent.blocks[self.i][self.j].treasure_class = tr_class


class CrushedBrickedBlock(Block):
    def __init__(self, parent, x, y, w, h, i, j, *groups):
        super().__init__(parent, x, y, w, h, i, j, *groups)
        self.image = tr.scale(load_image('Bricked_block_crushing.png'),
                              (self.w, self.h))
        self.crush_score = 200


class DeathBlock(Block):
    def __init__(self, parent, x, y, w, h, i, j, *groups):
        super().__init__(parent, x, y, w, h, i, j, *groups)
        self.image = tr.scale(load_image('Death_block.png'),
                              (self.w, self.h))
        self.crush_score = 600
        self.treasure_class = DeathTreasure
        self.collide_sound = self.parent.death_collide_sound

    def crush(self):
        self.treasure_class = DeathTreasure
        super().crush()


class ExplodingBlock(Block):
    def __init__(self, parent, x, y, w, h, i, j, *groups):
        super().__init__(parent, x, y, w, h, i, j, *groups)
        self.image = tr.scale(load_image('Exploding_block.png'),
                              (self.w, self.h))
        self.cur_index = 0
        self.frames = [self.image] + self.cut_frames(
            'Exploding_block_crushing_sprites.png', 6, 8)
        self.crush_score = 50
        self.collide_sound = self.parent.crush_sound

    def crush(self, only_self=False):
        if not only_self:
            for coords in self.get_neighbourhood_coords():
                i, j = coords
                self.parent.blocks[i][j].treasure_class = self.treasure_class
                if isinstance(self.parent.blocks[i][j], ExplodingBlock):
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
                                self.parent.temporary_group)

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
    def __init__(self, parent, x, y, w, h, place, *groups):
        super().__init__(*groups)
        self.parent = parent
        self.w, self.h = w, h
        self.image = tr.scale(load_image('Block_border.png'), (self.w, self.h))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.place = place

        self.mask = pg.mask.from_surface(self.image)
