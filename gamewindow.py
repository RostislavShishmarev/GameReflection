import pygame as pg
import pygame.transform as tr
import pygame.sprite as spr
import pygame.mixer as mix
import csv

from datetime import datetime as DateTime
from datetime import timedelta as TimeDelta
from functions import load_image, do_nothing, get_width
from widgets import Button, TextDisplay
from sprites import Platform, Triplex, Border
from blocks import Block, DeathBlock, ExplodingBlock, ScBlock, BrickedBlock


class GameWindow:
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
            g_over.image = load_image('game_over.png', -1)
            g_over.rect = g_over.image.get_rect()
            g_over.rect.topleft = (self.w // 2 - g_over.rect[2] // 2,
                                   self.h // 2 - g_over.rect[3] // 2)
            self.game_over_sound.play()
            self.GameWindow_ended = True
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
        self.new_window_after_self = GameWindow(self.parent,
                                          self.mod_name.split('_')[0] +\
                                          '_StartModel.csv')

    def no_blocks(self):
        return all([b is None or isinstance(b, ScBlock)
                    for row in self.blocks for b in row])


if __name__ == '__main__':
    window = GameWindow(None, 'DataBases/Level8_StartModel.csv')
    window.run()
