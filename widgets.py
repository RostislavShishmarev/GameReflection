import pygame as pg
import pygame.draw as dr
import pygame.transform as tr

from datetime import datetime as DateTime
from functions import do_nothing, get_width, load_image


class BaseWidget:
    def __init__(self, parent, rect):
        self.parent = parent
        x, y, w, h = rect
        self.x, self.y, self.x1, self.y1 = x, y, x + w, y + h
        self.w, self.h = w, h

    def render(self, screen=None):
        pass

    def __contains__(self, coords):
        return coords[0] in range(self.x, self.x1) and\
               coords[1] in range(self.y, self.y1)

    def process_event(self, event, *args, **kwargs):
        pass

    def set_coords(self, x, y):
        self.x, self.y = x, y
        self.x1, self.y1 = self.x + self.w, self.y + self.h

    def set_h(self, h):
        self.h = h
        self.x1 = self.x + h

    def set_w(self, w):
        self.w = w
        self.y1 = self.y + w


class HorAlign:
    LEFT = 'left'
    RIGHT = 'right'
    CENTER = 'center'


class Button(BaseWidget):
    def __init__(self, parent, rect, text, font_size=40,
                 main_color=pg.Color(70, 202, 232),
                 back_color=pg.Color(0, 0, 0), slot=do_nothing, text2=None,
                 key=None, modifier=None):
        super().__init__(parent, rect)
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
        self.border_w = 2

        self.key = key
        self.modifier = modifier

    def slot(self, *args, **kwargs):
        # Декорация переданной функции:
        self.current_text = self.text if self.current_text == self.text2\
            else self.text2

        self.function(*args, **kwargs)

    def render(self, screen=None):
        screen = screen if screen is not None else self.parent.screen
        dr.rect(screen, self.back_color,
                (self.x, self.y, self.w, self.h))
        dr.rect(screen, self.current_color,
                (self.x, self.y, self.w, self.h), width=self.border_w)
        font = pg.font.Font(None, self.font_size)
        text = font.render(self.current_text, True, self.current_color)
        screen.blit(text, (self.x + self.w // 2 - text.get_width() // 2,
                           self.y + self.h // 2 - text.get_height() // 2))

    def process_event(self, event, *args, **kwargs):
        if event.type == pg.MOUSEBUTTONDOWN:
            if event.pos in self:
                self.slot(*args, **kwargs)
        if event.type == pg.KEYDOWN and self.key is not None:
            if event.key == self.key:
                if self.modifier is not None:
                    if event.mod & self.modifier:
                        self.slot(*args, **kwargs)
                else:
                    self.slot(*args, **kwargs)
        if event.type == pg.MOUSEMOTION:
            if event.pos in self:
                self.current_color = self.light_main_color
            else:
                self.current_color = self.main_color

    def set_color(self, color):
        self.main_color = self.current_color = color
        self.light_main_color = pg.Color(min(self.main_color.r + 90, 255),
                                         min(self.main_color.g + 90, 255),
                                         min(self.main_color.b + 90, 255))

    def set_slot(self, slot):
        self.function = slot


class TextDisplay(BaseWidget):
    def __init__(self, parent, rect, title, text_item,
                 title_font_size=40, item_font_size=70,
                 main_color=pg.Color(239, 242, 46),
                 back_color=pg.Color(0, 0, 0), image_name=None):
        super().__init__(parent, rect)
        self.item = text_item
        self.title = title
        self.title_font_size = title_font_size
        self.item_font_size = item_font_size
        self.indent = 5
        self.main_color = main_color
        self.back_color = back_color
        self.border_w = 2
        self.border_radius = 8
        self.image_name = image_name

    def render(self, screen=None):
        screen = screen if screen is not None else self.parent.screen
        dr.rect(screen, self.back_color,
                (self.x, self.y, self.w, self.h),
                border_radius=self.border_radius)
        dr.rect(screen, self.main_color,
                (self.x, self.y, self.w, self.h), width=self.border_w,
                border_radius=self.border_radius)

        title_font = pg.font.Font(None, self.title_font_size)
        title = title_font.render(self.title, True, self.main_color)
        screen.blit(title, (self.x + self.w // 2 - title.get_width() // 2,
                            self.y + self.indent))

        item_font = pg.font.Font(None, self.item_font_size)
        item = item_font.render(self.item, True, self.main_color)
        item_x = self.x + self.w // 2 - item.get_width() // 2
        if self.image_name is not None:
            item_x = self.x + self.w - item.get_width() - self.w // 8
            im = tr.scale(load_image(self.image_name, -1), (5 * self.w // 8,
                                                            item.get_height()))
            screen.blit(im, (self.x + round(self.w // 8),
                        self.y + self.h - item.get_height() - 10))
        screen.blit(item, (item_x, self.y + self.h - item.get_height() - 5))

    def set_item(self, item):
        self.item = item


class TabWidget(BaseWidget):
    def __init__(self, parent, rect, titles, titles_h=40,
                 title_font_size=30,
                 main_color=pg.Color(20, 224, 54),
                 back_color=pg.Color(0, 0, 0)):
        super().__init__(parent, rect)
        self.main_color = main_color
        self.light_main_color = pg.Color(min(self.main_color.r + 90, 255),
                                         min(self.main_color.g + 90, 255),
                                         min(self.main_color.b + 90, 255))
        self.current_color = self.main_color
        self.back_color = back_color

        self.rects_w = 2
        self.bord_rad = 6
        self.text_indent = 10

        self.titles_names = titles
        self.selected_index = 0
        self.titles_h = titles_h
        self.title_font_size = title_font_size
        self.widgets = []
        x, y = self.x + 10, self.y
        for i, ttl in enumerate(self.titles_names):
            title_font = pg.font.Font(None, self.title_font_size)
            title = title_font.render(ttl, True, self.main_color)
            w, h = title.get_width() + self.text_indent * 2, self.titles_h
            self.widgets.append([[], Button(self.parent, (x, y, w, h), ttl,
                                            font_size=self.title_font_size,
                                            main_color=self.main_color,
                                            slot=self.change_selected)])
            x += w + self.rects_w * 2

    def render(self, screen=None):
        screen = screen if screen is not None else self.parent.screen
        dr.rect(screen, self.back_color,
                (self.x, self.y + self.titles_h - self.rects_w // 2,
                 self.w, self.h - self.titles_h + self.rects_w // 2),
                border_radius=self.bord_rad)
        dr.rect(screen, self.main_color,
                (self.x, self.y + self.titles_h - self.rects_w // 2,
                 self.w, self.h - self.titles_h + self.rects_w // 2),
                width=self.rects_w, border_radius=self.bord_rad)
        for i, title in enumerate(self.titles_names):
            self.widgets[i][1].render()
            if i == self.selected_index:
                self.surface = pg.Surface((self.w,
                                           self.h - self.titles_h +\
                                           self.rects_w // 2), pg.SRCALPHA, 32)
                self.surface.fill(pg.Color(0, 0, 0, 1))
                for widget in self.widgets[i][0]:
                    widget.render(screen=self.surface)
                pg.Surface.blit(screen, self.surface, (self.x,
                                                       self.y + self.titles_h -\
                                                       self.rects_w // 2))

    def process_event(self, event, *args, **kwargs):
        for i, title in enumerate(self.titles_names):
            self.widgets[i][1].process_event(event, i)
            for widget in self.widgets[i][0]:
                widget.process_event(event)

    def change_selected(self, index):
        self.selected_index = index
    
    def get_widgets(self, index):
        return self.widgets[index][0]

    def set_widgets(self, widgets, index):
        self.widgets[index][0] = widgets

    def add_widget(self, widget, index):
        self.widgets[index][0].append(widget)


class Image(BaseWidget):
    def __init__(self, parent, rect, image, proportional=False,
                 bord_color=None, light_image=None,
                 key=None, modifier=None, slot=do_nothing):
        super().__init__(parent, rect)
        if proportional:
            self.w = get_width(image, self.h)

        self.image = self.current_image = tr.scale(image, (self.w, self.h))
        self.light_image = light_image if light_image is None\
            else tr.scale(light_image, (self.w, self.h))

        self.key = key
        self.modifier = modifier
        self.slot = slot

        self.main_color = bord_color
        self.light_main_color = pg.Color(min(self.main_color.r + 90, 255),
                                         min(self.main_color.g + 90, 255),
                                         min(self.main_color.b + 90, 255))\
            if self.main_color is not None else None
        self.current_color = self.main_color
        self.border_w = 2

    def render(self, screen=None):
        screen = screen if screen is not None else self.parent.screen
        pg.Surface.blit(screen, self.current_image, (self.x, self.y))
        if self.current_color is not None:
            dr.rect(screen, self.current_color,
                    (self.x, self.y, self.w, self.h), width=self.border_w)

    def process_event(self, event, *args, **kwargs):
        if event.type == pg.MOUSEBUTTONDOWN:
            if event.pos in self:
                self.slot(*args, **kwargs)
        if event.type == pg.KEYDOWN and self.key is not None:
            if event.key == self.key:
                if self.modifier is not None:
                    if event.mod & self.modifier:
                        self.slot(*args, **kwargs)
                else:
                    self.slot(*args, **kwargs)
        if event.type == pg.MOUSEMOTION and self.light_image is not None:
            if event.pos in self:
                self.current_image = self.light_image
                self.current_color = self.light_main_color
            else:
                self.current_image = self.image
                self.current_color = self.main_color

    def set_image(self, image):
        self.image = self.current_image = image

    def set_color(self, color=None):
        self.main_color = self.current_color = color
        self.light_main_color = pg.Color(min(self.main_color.r + 90, 255),
                                         min(self.main_color.g + 90, 255),
                                         min(self.main_color.b + 90, 255))\
            if self.main_color is not None else None

    def set_slot(self, slot):
        self.slot = slot


class Label(BaseWidget):
    def __init__(self, parent, rect, text, main_color=pg.Color(247, 180, 10),
                 back_color=pg.Color(0, 0, 0), font_size=20, border=False,
                 alignment=HorAlign.LEFT, indent=5):
        super().__init__(parent, rect)
        self.text = text
        self.font_size = font_size
        self.alignment = alignment
        self.indent = indent
        self.main_color = main_color
        self.back_color = back_color
        self.border = border
        self.border_w = 2

    def render(self, screen=None):
        screen = screen if screen is not None else self.parent.screen
        if self.border:
            dr.rect(screen, self.back_color, (self.x, self.y, self.w, self.h))
            dr.rect(screen, self.main_color, (self.x, self.y, self.w, self.h),
                    width=self.border_w)
        font = pg.font.Font(None, self.font_size)
        text = font.render(self.text, True, self.main_color)
        if self.alignment == HorAlign.LEFT:
            x = self.x + self.indent
        elif self.alignment == HorAlign.CENTER:
            x = self.x + self.w // 2 - text.get_width() // 2
        elif self.alignment == HorAlign.RIGHT:
            x = self.x + self.w - self.indent
        else:
            return
        screen.blit(text, (x, self.y + self.h // 2 - text.get_height() // 2))

    def set_text(self, text):
        self.text = text

    def set_color(self, color):
        self.main_color = color


class ScrollList(BaseWidget):
    def __init__(self, parent, rect, title,
                 title_font_size=50, n_vizible=5,
                 main_color=pg.Color(245, 127, 17),
                 back_color=pg.Color(0, 0, 0)):
        super().__init__(parent, rect)
        self.main_color = main_color
        self.back_color = back_color

        self.rects_w = 2
        self.bord_rad = 6
        self.indent = 10
        self.n_vizible = n_vizible

        self.title = title
        self.title_font_size = title_font_size
        self.title_label = Label(self, (self.indent, self.indent,
                                        self.w - 2 * self.indent,
                                        self.title_font_size), self.title,
                                 font_size=self.title_font_size,
                                 main_color=self.main_color,
                                 alignment=HorAlign.CENTER)

        self.elements = []
        self.up_index = None
        self.selected_index = None

    def render(self, screen=None):
        screen = screen if screen is not None else self.parent.screen
        dr.rect(screen, self.back_color, (self.x, self.y, self.w, self.h),
                border_radius=self.bord_rad)
        dr.rect(screen, self.main_color, (self.x, self.y, self.w, self.h),
                width=self.rects_w, border_radius=self.bord_rad)

        self.surface = pg.Surface((self.w, self.h), pg.SRCALPHA, 32)
        self.surface.fill(pg.Color(0, 0, 0, 1))
        self.title_label.render(self.surface)
        if self.up_index is None:
            pg.Surface.blit(screen, self.surface, (self.x, self.y))
            return

        x, y = self.indent, 2 * self.indent + self.title_label.h
        els = self.elements[self.up_index:self.up_index + self.n_vizible]
        for i, el in enumerate(els):
            if self.up_index + i == self.selected_index:
                el.set_selected(True)
            else:
                el.set_selected(False)
            el.set_coords(x, y)
            el.set_number(self.up_index + i + 1)
            el.render(self.surface)
            y += self.indent + el.h
        pg.Surface.blit(screen, self.surface, (self.x, self.y))

    def process_event(self, event, *args, **kwargs):
        if self.up_index is None:
            return
        if event.type == pg.MOUSEWHEEL:
            if pg.mouse.get_pos() in self:
                self.change_up(1 if event.y < 0 else -1)
        if event.type == pg.MOUSEBUTTONDOWN:
            if event.button == 1 and\
                            self.trans_pos(event.pos) in self.title_label:
                self.selected_index = None
        els = self.elements[self.up_index:self.up_index + self.n_vizible]
        for i, el in enumerate(els):
            self.elements[self.up_index + i].process_event(event)

    def change_up(self, delta):
        new_index = self.up_index + delta
        if 0 <= new_index < len(self.elements) - self.n_vizible + 2:
            self.up_index = new_index

    def set_elements(self, elements, but_image=None, but_light_image=None,
                     but_slot=do_nothing, select_func=do_nothing):
        self.elements = []
        h = (self.h - 3 * self.indent + self.title_label.h) //\
            self.n_vizible - self.indent
        for i, el in enumerate(elements):
            item, info = el
            self.elements.append(ScrollElement(self,
                                               (0, 0, self.w - self.indent * 2,
                                                h), item, but_image=but_image,
                                               but_light_image=but_light_image,
                                               but_slot=but_slot,
                                               information=info,
                                               select_func=select_func))
        self.up_index = None if elements == [] else 0
        self.selected_index = None if elements == [] else self.selected_index

    def trans_pos(self, pos):
        '''Трансформирует абсолютную точку в относительную для дочерних
 элементов'''
        return (pos[0] - self.x, pos[1] - self.y)

    def get_selected_item_info(self):
        if self.selected_index is None:
            return
        return self.elements[self.selected_index].get_info()

    def get_selected_item_index(self):
        return self.selected_index


class ScrollElement(BaseWidget):
    def __init__(self, parent, rect, text_item, font_size=35,
                 but_image=None, but_light_image=None, but_slot=do_nothing,
                 main_color=pg.Color(245, 127, 17),
                 back_color=pg.Color(20, 20, 20), information=None,
                 select_func=do_nothing):
        super().__init__(parent, rect)
        self.text = text_item
        self.font_size = font_size
        self.information = information

        self.but_image = but_image
        self.but_light_image = but_light_image
        self.but_slot = but_slot
        self.select_function = select_func

        self.main_color = self.current_color = main_color
        self.light_main_color = pg.Color(min(self.main_color.r + 90, 255),
                                         min(self.main_color.g + 90, 255),
                                         min(self.main_color.b + 90, 255))
        self.back_color = back_color

        self.indent = 5
        self.rects_w = 3
        self.bord_rad = 0
        self.number = 1
        self.selected = False
        self.button = None

        item_w = self.w - self.y - self.indent * 2
        if self.but_image is not None:
            item_w -= self.h + self.indent * 2
            self.button = Image(self, (self.h + self.indent * 3 + item_w,
                                       self.indent, self.h - self.indent * 2,
                                       self.h - self.indent * 2),
                                load_image(self.but_image),
                                light_image=self.but_light_image,
                                slot=self.but_slot)
        self.item_label = Label(self, (self.h + 2 * self.indent, self.indent,
                                       item_w, self.h - self.indent * 2),
                                self.text, main_color=self.current_color,
                                 back_color=self.back_color,
                                font_size=self.font_size)
        self.num_label = Label(self, (self.indent, self.indent,
                                      self.h - self.indent * 2,
                                      self.h - self.indent * 2),
                                str(self.number),
                                main_color=self.current_color,
                                back_color=self.back_color,
                                alignment=HorAlign.CENTER,
                                font_size=self.font_size)


    def render(self, screen=None, index=0):
        screen = screen if screen is not None else self.parent.screen
        dr.rect(screen, self.back_color, (self.x, self.y, self.w, self.h),
                border_radius=self.bord_rad)
        dr.rect(screen, self.current_color, (self.x, self.y, self.w, self.h),
                width=self.rects_w, border_radius=self.bord_rad)

        self.surface = pg.Surface((self.w, self.h), pg.SRCALPHA, 32)
        self.surface.fill(pg.Color(0, 0, 0, 1))
        dr.ellipse(self.surface, self.current_color, (self.indent, self.indent,
                                                   self.h - self.indent * 2,
                                                   self.h - self.indent * 2),
                   width=self.rects_w)
        self.num_label.render(self.surface)
        self.item_label.render(self.surface)
        if self.button is not None:
            self.button.render(self.surface)
        pg.Surface.blit(screen, self.surface, (self.x, self.y))

    def set_selected(self, bool_obj):
        self.selected = bool_obj
        color = self.light_main_color if self.selected\
            else self.main_color
        self.current_color = color
        self.num_label.set_color(self.current_color)
        self.item_label.set_color(self.current_color)

    def get_info(self):
        return self.information

    def set_number(self, num):
        self.number = num
        self.num_label.set_text(str(self.number))

    def process_event(self, event, *args, **kwargs):
        if event.type == pg.MOUSEBUTTONDOWN:
            if self.parent.trans_pos(event.pos) in self and event.button == 1:
                self.parent.selected_index = self.number - 1
                self.select_function()


class ResultsTextDisplay(BaseWidget):
    def __init__(self, parent, rect, score=0, time=(0, 0), victories=0,
                 defeats=0, item_font_size=25, title_font_size=30,
                 main_color=pg.Color(239, 242, 46),
                 back_color=pg.Color(0, 0, 0)):
        super().__init__(parent, rect)
        self.score, self.time = score, time
        self.victories, self.defeats = victories, defeats
        self.title_font_size = title_font_size
        self.item_font_size = item_font_size
        self.indent = 10
        self.main_color = main_color
        self.back_color = back_color
        self.border_w = 2
        self.border_radius = 0
        self.title_labels = [Label(self, (0, 0, self.w // 3, self.h // 3),
                                   'Рекорды:', main_color=self.main_color,
                                   alignment=HorAlign.CENTER,
                                   font_size=self.title_font_size),
                             Label(self, (self.w // 3, 0, self.w // 3,
                                          self.h // 3),
                                   'Побед:', main_color=self.main_color,
                                   alignment=HorAlign.CENTER,
                                   font_size=self.title_font_size),
                             Label(self, (2 * self.w // 3, 0, self.w // 3,
                                          self.h // 3),
                                   'Поражений:', main_color=self.main_color,
                                   alignment=HorAlign.CENTER,
                                   font_size=self.title_font_size)]
        games_font = get_max_font_size(str(max((self.victories,
                                                self.defeats))), self.w // 3,
                                       start_font=60)
        self.const_labels = [Label(self, (0, self.h // 3, self.w // 6,
                                          self.h // 3), 'Очки:',
                                   main_color=self.main_color,
                                   alignment=HorAlign.CENTER,
                                   font_size=self.item_font_size),
                             Label(self, (0, self.h // 3 * 2, self.w // 6,
                                          self.h // 3),'Время:',
                                   main_color=self.main_color,
                                   alignment=HorAlign.CENTER,
                                   font_size=self.item_font_size),
                             Label(self, (self.w // 3, self.h // 3,
                                          self.w // 3, self.h // 3 * 2),
                                   str(self.victories),
                                   main_color=self.main_color,
                                   alignment=HorAlign.CENTER,
                                   font_size=games_font),
                             Label(self, (self.w // 3 * 2, self.h // 3,
                                          self.w // 3, self.h // 3 * 2),
                                   str(self.defeats),
                                   main_color=self.main_color,
                                   alignment=HorAlign.CENTER,
                                   font_size=games_font)]
        self.score_label = Label(self, (self.w // 6, self.h // 3, self.w // 6,
                                          self.h // 3), str(self.score),
                                main_color=self.main_color,
                                alignment=HorAlign.CENTER,
                                font_size=self.item_font_size)
        self.time_label = Label(self, (self.w // 6, self.h // 3 * 2,
                                       self.w // 6, self.h // 3),
                                str_time(self.time),
                                main_color=self.main_color,
                                alignment=HorAlign.CENTER,
                                font_size=self.item_font_size)

    def render(self, screen=None):
        screen = screen if screen is not None else self.parent.screen
        dr.rect(screen, self.back_color,
                (self.x, self.y, self.w, self.h),
                border_radius=self.border_radius)
        dr.rect(screen, self.main_color,
                (self.x, self.y, self.w, self.h), width=self.border_w,
                border_radius=self.border_radius)
        self.surface = pg.Surface((self.w, self.h), pg.SRCALPHA, 32)
        self.surface.fill(pg.Color(0, 0, 0, 1))
        for lab in self.title_labels + self.const_labels:
            lab.render(self.surface)
        self.score_label.render(self.surface)
        self.time_label.render(self.surface)
        pg.Surface.blit(screen, self.surface, (self.x, self.y))

    def set_records(self, score=0, time=(0, 0)):
        self.score = score
        self.time = time
        self.score_label.set_text(str(self.score))
        self.time_label.set_text(str_time(self.time))


def get_max_font_size(text, w, start_font=200):
    while True:
        text_font = pg.font.Font(None, start_font)
        text_sc = text_font.render(text, True, pg.Color(0, 0, 0))
        if text_sc.get_width() < w:
            return start_font
        start_font -= 1


def str_time(time_tuple):
    time = DateTime(2020, 1, 1, 1, *time_tuple)
    return time.strftime('%M:%S')
