import pygame as pg
import pygame.transform as tr
import pygame.sprite as spr
from functions import load_image, get_width


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
        if (self.vy > -1 and self.vy < 1) and self.vx != 0:
            self.vy += 1

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
