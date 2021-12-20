import pygame
import sys
from pygame.locals import *
import pygame as pg
import pygame.image as img
import pygame.draw as dr
import pygame.transform as tr
import pygame.sprite as spr
import csv
from datetime import datetime as DateTime
from datetime import timedelta as TimeDelta
import os


class Game:
    def __init__(self, csv_model_name, score, time, lifes):
        pass


class MainWindow:
    def __init__(self):
        pygame.init()
        #Экран
        size = width, height = 1240, 700
        screen = pygame.display.set_mode(size, HWSURFACE | DOUBLEBUF | RESIZABLE)
        #Иконка
        pg.display.set_caption('Отражение')
        pg.display.set_icon(self.load_image('Reflection_logo_2.png'))
        #Флаг
        pygame.mouse.set_visible(False)
        #Цикл
        while pygame.event.wait().type != pygame.QUIT:
            #Фон
            win = pygame.display.get_surface()
            x = win.get_width()
            y = win.get_height()
            fone1 = tr.scale(self.load_image('Fone.png'), (x, y))
            # Курсор
            image = self.load_image('Cursor.png')
            cursor_img_rect = image.get_rect()
            cursor_img_rect.center = pygame.mouse.get_pos()
            screen.blit(image, cursor_img_rect)
            #Фон и кнопки
            pygame.display.flip()
            screen.blit(fone1, (0, 0))
            self.draw(screen, x - 140, y - 55)
        pygame.quit()

    def load_image(self, name, colorkey=None):
        fullname = os.path.join('Images', name)
        # если файл не существует, то выходим
        if not os.path.isfile(fullname):
            print(f"Файл с изображением '{fullname}' не найден")
            sys.exit()
        image = pygame.image.load(fullname)
        return image

    def draw(self, screen, x, y):
        font = pygame.font.Font(None, 50)
        text = font.render("Выход", True, (100, 255, 100))
        text_x = x
        text_y = y
        text_w = text.get_width()
        text_h = text.get_height()
        pygame.draw.rect(screen, (100, 255, 100), (text_x - 10, text_y - 10, text_w + 20, text_h + 20), 1)
        screen.blit(text, (text_x, text_y))



if __name__ == '__main__':
    Window = MainWindow()