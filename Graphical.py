import pygame


class Pygame_Window:
    def __init__(self):
        pygame.font.init()
        WIDTH = 1500
        HEIGHT = 800
        self.WIN = pygame.display.set_mode((WIDTH, HEIGHT))

    def draw(self):
        self.WIN.fill((0, 0, 0))
        pygame.display.update()
