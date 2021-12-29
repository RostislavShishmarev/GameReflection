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



class Levels:
    def __init__(self, screen, width, height):
        self.screen = screen
        self.x = width
        self.y = height

    def buttons_lvl(self):
        n = 55
        for i in range(2):
            Buttons(self.screen, self.x + n, self.y + n, text='Уровень {}'.format(i + 1),
                    text_color=(255, 91, 0), light_text_color=(255, 181, 90), back_color=(0, 0, 0), light_back_color=(20, 20, 20)).text_btn()
            n += 75

    def window_lvl(self):
        font = pygame.font.Font(None, 50)
        text = font.render("Уровни", True, (255, 91, 0))
        w = text.get_width()
        h = text.get_height()
        pygame.draw.rect(self.screen, (0, 0, 0), (self.x - 5, self.y - 10, w + 250, h + 490), border_radius=8)
        table = pg.draw.rect(self.screen, (255, 91, 0), (self.x - 5, self.y - 10, w + 250, h + 490), 2, border_radius=8)
        self.screen.blit(text, (self.x + 120, self.y))



class Buttons:
    def __init__(self, screen, width, height, color=None,
                 light_color=None, image_size=None, image=None, light_image=None, text=None,
                 text_color=None, light_text_color=None, back_color=None, light_back_color=None):
        self.screen = screen
        self.x = width
        self.y = height
        if image is not None:
            self.color = color
            self.light_color = light_color
            self.image = image
            self.light_image = light_image
            self.image_size = image_size
        if text is not None:
            self.text = text
            self.text_color = text_color
            self.light_text_color = light_text_color
            self.back_color = back_color
            self.light_back_color = light_back_color

    def image_btn(self):
        settings = tr.scale(load_image(self.image), self.image_size)
        settings1 = tr.scale(load_image(self.light_image), self.image_size)
        w = settings.get_width()
        h = settings.get_height()
        rect = pygame.draw.rect(self.screen, self.color, (self.x - 2, self.y - 2, w + 4, h + 4), 2)
        self.screen.blit(settings, (self.x, self.y))
        if rect.collidepoint(pg.mouse.get_pos()):
            pygame.draw.rect(self.screen, self.light_color, (self.x - 2, self.y - 2, w + 4, h + 4), 2)
            self.screen.blit(settings1, (self.x, self.y))
        return rect
        # цвет - (100, 255, 100), цвет2 - (70, 202, 232)

    def text_btn(self):
        font = pygame.font.Font(None, 50)
        text = font.render(self.text, True, self.text_color)
        text1 = font.render(self.text, True, self.light_text_color)
        w = text.get_width()
        h = text.get_height()
        pygame.draw.rect(self.screen, self.back_color, (self.x - 10, self.y - 10, w + 20, h + 25))
        rect = pygame.draw.rect(self.screen, self.text_color, (self.x - 10, self.y - 10, w + 20, h + 25), 2)
        self.screen.blit(text, (self.x, self.y))
        if rect.collidepoint(pg.mouse.get_pos()):
                pygame.draw.rect(self.screen, self.light_back_color, (self.x - 10, self.y - 10, w + 20, h + 25))
                pygame.draw.rect(self.screen, self.light_text_color, (self.x - 10, self.y - 10, w + 20, h + 25), 2)
                self.screen.blit(text1, (self.x, self.y))
        return rect



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
        pg.display.set_icon(load_image('Reflection_logo.png'))
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
                rect_set = Buttons(screen, self.width - 105, self.height - 690, color=(100, 255, 100), light_color=(150, 255, 150),
                                   image_size=(90, 90), image='Settings.png', light_image='Settings_light.png').image_btn()
                if rect_set.collidepoint(pg.mouse.get_pos()):
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        pass
                # Кнопка игры
                rect_play = Buttons(screen, self.width - 220, self.height - 66, text='Играть',
                                    text_color=(70, 202, 232), light_text_color=(160, 255, 255),
                                    back_color=(0, 0, 0), light_back_color=(20, 20, 20)).text_btn()
                if rect_play.collidepoint(pg.mouse.get_pos()):
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        pass
                # Кнопка выхода
                rect_exit = Buttons(screen, self.width - 75, self.height - 75, color=(70, 202, 232), light_color=(160, 255, 255),
                                   image_size=(56, 56), image='Exit.png', light_image='Exit_light.png').image_btn()
                if rect_exit.collidepoint(pg.mouse.get_pos()):
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        self.running = False
                #Линия
                pygame.draw.line(screen, (255, 255, 255), [0, 150], [1240, 150], 2)
                #Уровни
                Levels(screen, self.width - 1220, self.height - 530).window_lvl()
                Levels(screen, self.width - 1220, self.height - 530).buttons_lvl()
        pygame.quit()



if __name__ == '__main__':
    Window = MainWindow()
    Window.run()