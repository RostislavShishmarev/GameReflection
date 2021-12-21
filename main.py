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

def load_image(name):
    fullname = os.path.join('Images', name)
    # если файл не существует, то выходим
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    return image



class MainWindow:
    def __init__(self):
        pygame.init()
        #Экран
        size = width, height = 1240, 700
        screen = pygame.display.set_mode(size, RESIZABLE)
        fone1 = tr.scale(load_image('Fone.png'), (1707, 1004))
        #Иконка
        pg.display.set_caption('Отражение')
        pg.display.set_icon(load_image('Reflection_logo_2.png'))
        #Флаг
        pygame.mouse.set_visible(False)
        running = True
        #Цикл
        while running:
            for event in pygame.event.get():
                # при закрытии окна
                if event.type == pygame.QUIT:
                    running = False
                #Окно
                win = pygame.display.get_surface()
                x = win.get_width()
                y = win.get_height()
                # Курсор
                if pg.mouse.get_focused():
                    image = load_image('Cursor.png')
                    cursor_img_rect = image.get_rect()
                    cursor_img_rect.center = pygame.mouse.get_pos()
                    screen.blit(image, cursor_img_rect)
                #Фон и кнопки
                pygame.display.flip()
                screen.blit(fone1, (0, 0))
                self.exit_btn(screen, x - 75, y - 75)
                if pg.mouse.get_pos()[0] >= x - 75 and pg.mouse.get_pos()[1] >= y - 75:
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        running = False
        pygame.quit()

    def exit_btn(self, screen, x, y):
        exit = tr.scale(load_image('Exit.png'), (56, 56))
        exit1 = tr.scale(load_image('Exit_light.png'), (56, 56))
        w = exit.get_width()
        h = exit.get_height()
        pygame.draw.rect(screen, ((70, 202, 232)), (x - 2, y - 2, w + 4, h + 4), 2)
        screen.blit(exit, (x, y))
        if pg.mouse.get_pos()[0] >= x and pg.mouse.get_pos()[1] >= y:
            pygame.draw.rect(screen, ((160, 255, 255)), (x - 2, y - 2, w + 4, h + 4), 2)
            screen.blit(exit1, (x, y))
        #цвет - (100, 255, 100), цвет2 - (70, 202, 232)



if __name__ == '__main__':
    Window = MainWindow()