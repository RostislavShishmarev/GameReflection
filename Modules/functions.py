import pygame as pg
import pygame.transform as tr
import os

from datetime import datetime as DateTime


def load_image(name, color_key=None):
    fullname = 'Images/' + name
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


def get_height(surface, width):
    return round(surface.get_size()[1] * (width / surface.get_size()[0]))


def get_fone(fone_image, window_width, window_height, coef=1.01):
    w, h = fone_image.get_width(), fone_image.get_height()
    while True:
        if round(w) >= window_width and round(h) >= window_height:
            return tr.scale(fone_image, (round(w), round(h)))
        w *= coef
        h *= coef


def get_max_font_size(text, w, start_font=200):
    while True:
        text_font = pg.font.Font(None, start_font)
        text_sc = text_font.render(text, True, pg.Color(0, 0, 0))
        if text_sc.get_width() < w:
            return start_font
        start_font -= 1


def str_time(time_tuple):
    return make_tuple_time(time_tuple).strftime('%M:%S')


def make_tuple_time(time_tuple):
    return DateTime(2020, 1, 1, 1, *time_tuple)
