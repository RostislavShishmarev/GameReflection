import pygame as pg
import pygame.sprite as spr
import pygame.transform as tr

from Modules.functions import load_image


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
        self.parent.temporary_group.remove(self)

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
