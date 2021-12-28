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
        self.size = self.width, self.height = 1240, 700
        self.fone = tr.scale(load_image('Fone.png'), (1240, 700))
        self.cursor = load_image('Cursor.png')
        self.cursor_img_rect = self.cursor.get_rect()
        # Флаг
        self.running = True

    def run(self):
        pygame.init()
        # Экран
        screen = pygame.display.set_mode(self.size)
        # Иконка
        pg.display.set_caption('Отражение')
        pg.display.set_icon(load_image('Reflection_logo_2.png'))
        # Флаг
        pygame.mouse.set_visible(False)
        # Цикл
        while self.running:
            for event in pygame.event.get():
                # при закрытии окна
                if event.type == pygame.QUIT:
                    self.running = False
                # Курсор
                if pg.mouse.get_focused():
                    self.cursor_img_rect.center = pygame.mouse.get_pos()
                    screen.blit(self.cursor, self.cursor_img_rect)
                # Фон
                pygame.display.flip()
                screen.blit(self.fone, (0, 0))
                # Кнопка настроек
                self.settings_btn(screen, self.width - 105, self.height - 690)
                if self.rect_set.collidepoint(pg.mouse.get_pos()):
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        pass
                # Кнопка игры
                self.play_btn(screen, self.width - 220, self.height - 66)
                if self.rect1.collidepoint(pg.mouse.get_pos()):
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        pass
                # Кнопка выхода
                self.exit_btn(screen, self.width - 75, self.height - 75)
                if self.rect.collidepoint(pg.mouse.get_pos()):
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        self.running = False
                #Линия
                pygame.draw.line(screen, (255, 255, 255), [0, 150], [1240, 150], 2)
                #Уровни
                self.levels(screen, self.width - 1220, self.height - 530, 10)
        pygame.quit()

    def levels(self, screen, x, y, level):
        font = pygame.font.Font(None, 50)
        text = font.render("Уровни", True, (255, 91, 0))
        w = text.get_width()
        h = text.get_height()
        pygame.draw.rect(screen, (0, 0, 0), (x - 5, y - 10, w + 250, h + 490), border_radius=8)
        table = pg.draw.rect(screen, (255, 91, 0), (x - 5, y - 10, w + 250, h + 490), 2, border_radius=8)
        screen.blit(text, (x + 120, y))

    def settings_btn(self, screen, x, y):
        settings = tr.scale(load_image('Settings.png'), (90, 90))
        settings1 = tr.scale(load_image('Settings_light.png'), (90, 90))
        w = settings.get_width()
        h = settings.get_height()
        self.rect_set = pygame.draw.rect(screen, (100, 255, 100), (x - 2, y - 2, w + 4, h + 4), 2)
        screen.blit(settings, (x, y))
        if self.rect_set.collidepoint(pg.mouse.get_pos()):
            pygame.draw.rect(screen, (150, 255, 150), (x - 2, y - 2, w + 4, h + 4), 2)
            screen.blit(settings1, (x, y))

    def play_btn(self, screen, x, y):
        font = pygame.font.Font(None, 50)
        text = font.render("Играть", True, (70, 202, 232))
        text1 = font.render("Играть", True, (160, 255, 255))
        w = text.get_width()
        h = text.get_height()
        pygame.draw.rect(screen, (0, 0, 0), (x - 10, y - 10, w + 20, h + 25))
        self.rect1 = pygame.draw.rect(screen, (70, 202, 232), (x - 10, y - 10, w + 20, h + 25), 2)
        screen.blit(text, (x, y))
        if self.rect1.collidepoint(pg.mouse.get_pos()):
                pygame.draw.rect(screen, (20, 20, 20), (x - 10, y - 10, w + 20, h + 25))
                pygame.draw.rect(screen, (160, 255, 255), (x - 10, y - 10, w + 20, h + 25), 2)
                screen.blit(text1, (x, y))

    def exit_btn(self, screen, x, y):
        exit = tr.scale(load_image('Exit.png'), (56, 56))
        exit1 = tr.scale(load_image('Exit_light.png'), (56, 56))
        w = exit.get_width()
        h = exit.get_height()
        self.rect = pygame.draw.rect(screen, (70, 202, 232), (x - 2, y - 2, w + 4, h + 4), 2)
        screen.blit(exit, (x, y))
        if self.rect.collidepoint(pg.mouse.get_pos()):
            pygame.draw.rect(screen, (160, 255, 255), (x - 2, y - 2, w + 4, h + 4), 2)
            screen.blit(exit1, (x, y))
        #цвет - (100, 255, 100), цвет2 - (70, 202, 232)



if __name__ == '__main__':
    Window = MainWindow()
    Window.run()