import pygame as pg
import pygame.transform as tr
import pygame.sprite as spr
import pygame.mixer as mix
import sqlite3
import csv
import os

from datetime import datetime as DateTime
from datetime import timedelta as TimeDelta
from math import floor
from functions import load_image, do_nothing, get_width, str_time,\
    make_tuple_time
from widgets import Button, TextDisplay, Image, Label, ScrollList,\
    ResultsTextDisplay
from sprites import Platform, Triplex, Border
from blocks import Block, DeathBlock, ExplodingBlock, ScBlock, BrickedBlock,\
    CrushedBrickedBlock


class InfoWindow:
    def __init__(self):
        # Задаём атрибуты:
        self.FPS = 30
        self.size = (self.w, self.h) = (1400, 800)
        self.indent = 15
        self.up_indent = 80
        self.rules_font = 30

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
        logo = load_image('Reflection_logo.png')
        pg.display.set_icon(logo)

        # Создаём спрайты:
        self.cursor = spr.Sprite(self.cursor_group)
        self.cursor.image = load_image("cursor.png")
        self.cursor.rect = self.cursor.image.get_rect()

        # Создаём виджеты:
        logo_w = get_width(logo, self.up_indent)
        logo_color = pg.Color(0, 162, 232)
        self.logo_widgets = [Image(self, (self.indent, self.indent,
                                          logo_w, self.up_indent),
                                   logo, bord_color=logo_color),
                             Label(self, (self.indent * 2 + logo_w,
                                          self.indent, 400, self.up_indent),
                                   'Правила игры',
                                    font_size=60,
                                    alignment=HorAlign.LEFT,
                                    main_color=logo_color)]
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
        rules_w = self.tab_widget.get_surface_size()[0] - 2 * self.indent
        rules_h = self.tab_widget.get_surface_size()[1] - 2 * self.indent
        self.tab_widget.add_widget(Image(self, (self.indent, self.indent,
                                                rules_w, rules_h),
                                         load_image('Main_rules.png')), 0)
        self.tab_widget.add_widget(Image(self, (self.indent, self.indent,
                                                rules_w, rules_h),
                                         load_image('Blocks_rules.png')), 1)
        self.tab_widget.add_widget(Image(self, (self.indent, self.indent,
                                                rules_w, rules_h),
                                         load_image('Treasures_rules.png')), 2)

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
            for lab in self.logo_widgets:
                lab.render()
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


class GameWindow:
    def __init__(self, parent, csv_model_name,
                 score=0, time=(0, 0), lifes=4):
        # Задаём атрибуты:
        self.blocks_dict = {'nothing': None, 'Block.png': Block,
                            'Sc_block.png': ScBlock,
                            'Bricked_block.png': BrickedBlock,
                            'Death_block.png': DeathBlock,
                            'Exploding_block.png': ExplodingBlock,
                            'Bricked_block_crushing.png': CrushedBrickedBlock}
        self.blocks_code_dict = {'Block': 'Block.png',
                                 'ScBlock': 'Sc_block.png',
                                 'BrickedBlock': 'Bricked_block.png',
                                 'DeathBlock': 'Death_block.png',
                                 'ExplodingBlock': 'Exploding_block.png',
                                 'CrushedBrickedBlock':
                                     'Bricked_block_crushing.png'}

        self.parent = parent
        self.mod_name = csv_model_name
        self.level_id = int(self.mod_name.split('/')[-1].split('_')[0][5:])
        self.score = score
        self.time = make_tuple_time(time)
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
        self.buttons = [Button(self, (20, self.h - 60, 350, 50),
                               'Сохранить', slot=self.save,
                               key=pg.K_s, modifier=pg.KMOD_CTRL),
                        Button(self, (self.w // 2 - 175, self.h - 60, 350, 50),
                               'Пауза', slot=self.change_pause,
                               text2='Продолжить', key=pg.K_SPACE),
                        Button(self, (self.w - 370, self.h - 60, 350, 50),
                               'Выход', slot=self.exit,
                               key=pg.K_HOME, modifier=pg.KMOD_CTRL)]
        self.displays = [TextDisplay(self, (20, 10, 300, 100),
                                     'Очки', str(self.score)),
                         TextDisplay(self, (self.w // 2 - 150, 10, 300, 100),
                                     'Жизни', str(self.lifes),
                                     image_name='Platform.png'),
                         TextDisplay(self, (self.w - 320, 10, 300, 100),
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
                        if self.time >= make_tuple_time((59, 59)):
                            self.lifes = 0
                            self.begin_die()
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
        self.new_window_after_self = MainWindow()

    def save(self):
        files = os.listdir('DataBases')
        n_savings = len([f for f in files
                         if f.startswith(self.mod_name.split('/')[-1].split(
                '_')[0]) and
                         f.split('_')[1].startswith(self.parent.nik)])
        name = self.mod_name.split('_')[0] + '_' + self.parent.nik +\
               str(n_savings + 1) + '.csv'
        with open(name, mode='w', encoding='utf8', newline='') as f:
            wr = csv.writer(f, delimiter=';', quotechar='"')
            for row in self.blocks:
                mod_row = []
                for b in row:
                    if b is None:
                        mod_row.append('nothing')
                    else:
                        code_name = self.blocks_code_dict[b.__class__.__name__]
                        mod_row.append(code_name)
                wr.writerow(mod_row)
        cur = self.parent.db.cursor()
        time = str(self.time.minute) + ' ' + str(self.time.second)
        saving_time = DateTime.today().strftime('%d-%m-%Y %H:%M:%S')
        cur.execute('''INSERT INTO savings(level_id, model_way, lifes, score,
 time, saving_time) VALUES(?, ?, ?, ?, ?,
 ?)''', (int(self.mod_name.split('/')[-1].split('_')[0][5:]), name,
         self.lifes, self.score, time, saving_time))
        self.parent.db.commit()

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

            cur = self.parent.db.cursor()
            cur.execute('''UPDATE user SET defeats = defeats + 1''')
            self.parent.db.commit()
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

        cur = self.parent.db.cursor()
        cur.execute('''UPDATE user SET victories = victories + 1''')
        old_scr, old_time = cur.execute('''SELECT score, time FROM
 levels WHERE id = ?''', (self.level_id, )).fetchone()
        if old_scr is None or int(self.score) > int(old_scr):
            cur.execute('''UPDATE levels SET score = ? WHERE id = ?''',
                        (self.score, self.level_id))
        if old_time is None or self.time <\
                make_tuple_time([int(el) for el in old_time.split()]):
            cur.execute('''UPDATE levels SET time = ? WHERE id = ?''',
                        (str(self.time.minute) + ' ' + str(self.time.second),
                        self.level_id))

        cur.execute('''UPDATE levels SET opened = 'True' WHERE id = ?''',
                    (self.level_id + 1, ))
        self.parent.db.commit()

    def restart(self):
        self.exit()
        self.new_window_after_self = GameWindow(self.parent,
                                          self.mod_name.split('_')[0] +\
                                          '_StartModel.csv')

    def no_blocks(self):
        return all([b is None or isinstance(b, ScBlock)
                    for row in self.blocks for b in row])


class MainWindow:
    def __init__(self):
        # Задаём атрибуты:
        self.FPS = 80
        self.size = (self.w, self.h) = (1300, 760)
        self.indent = 15

        self.db = sqlite3.connect('DataBases/Reflection_db.db3')
        cur = self.db.cursor()
        levels = cur.execute('''SELECT name, way, score, time, id, opened
 FROM levels''').fetchall()
        self.levels = [(lv[0], lv[1:5]) for lv in levels if lv[-1]]
        (self.nik, self.victs, self.defs) = cur.execute('''SELECT nik,
 victories, defeats FROM user''').fetchone()
        self.photos_names = ['User_cat.jpg', 'User_bear.jpg',
                             'User_dragon2.jpg', 'User_phoenix.jpg']
        self.photo_index = floor(len(self.levels) / len(levels) *\
                                 (len(self.photos_names) - 0.1))

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
                              slot=self.open_settings, modifier=pg.KMOD_ALT,
                              key=pg.K_s),
                        Button(self, (self.w - 2 * self.indent - play_h - play_w,
                                      self.h - self.indent - play_h, play_w,
                                      play_h), 'Играть',
                               slot=self.open_gamewindow, font_size=60),
                        Image(self, (self.w - self.indent - play_h,
                                     self.h - self.indent - play_h,
                                     play_h, play_h), load_image('Exit.png'),
                              light_image=load_image('Exit_light.png'),
                              bord_color=pg.Color(70, 202, 232),
                              slot=self.exit, modifier=pg.KMOD_CTRL,
                              key=pg.K_HOME)]

        levels_w = 375
        self.levels_widget = ScrollList(self, (self.indent,
                                        user_h + user_font + self.indent * 3,
                                        levels_w,
                                        self.h - user_h - user_font -\
                                        self.indent * 4), 'Уровни',
                                 n_vizible=7, select_func=self.update_window)
        self.levels_widget.set_elements(self.levels)

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
                                                 user_h + user_font),
                                          victories=self.victs,
                                          defeats=self.defs)

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
 time, lifes, id FROM savings WHERE level_id =
 ?''', (self.levels_widget.get_selected_item_info()[-1], )).fetchall()
            im = load_image('Delete.png', -1)
            light_im = load_image('Delete_light.png', -1)
            self.savings_widget.set_elements([(sav[0], sav[1:])
                                              for sav in savings],
                                             but_image=im,
                                             but_light_image=light_im,
                                             but_slot=self.delete_saving)
        except TypeError as ex:
            self.savings_widget.set_elements([])
        records = self.levels_widget.get_selected_item_info()
        if records is not None:
            score, time = records[1:3]
            if score is not None and time is not None:
                time = (int(time.split()[0]), int(time.split()[1]))
                self.results.set_records(score, time)
                return
        self.results.set_records()

    def exit(self):
        self.running = False

    def delete_saving(self):
        if self.savings_widget.get_selected_item_info() is None:
            return
        id = self.savings_widget.get_selected_item_info()[-1]
        cur = self.db.cursor()
        model_name = cur.execute('''SELECT model_way FROM savings
 WHERE id = ?''', (id, )).fetchone()[0]
        os.remove(model_name)
        cur.execute('''DELETE FROM savings WHERE id = ?''', (id, ))
        self.db.commit()
        self.update_window()

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
        model, score, time, lifes = saving[:4]
        time = (int(time.split()[0]), int(time.split()[1]))
        self.exit()
        self.new_window_after_self = GameWindow(self, model, score,
                                                time, lifes)


if __name__ == '__main__':
    window = MainWindow()
    window.run()
