import pygame
from settings import GREEN, BROWN, WIDTH, HEIGHT

class GameMap:
    def __init__(self):
        self.path = [
            (0, 350),
            (200, 350),
            (200, 200),
            (500, 200),
            (500, 500),
            (900, 500),
            (900, 300),
            (WIDTH, 300)
        ]

        self.path_width = 50

    def draw(self, screen):
        screen.fill(GREEN)

        for i in range(len(self.path) - 1):
            pygame.draw.line(
                screen,
                BROWN,
                self.path[i],
                self.path[i + 1],
                self.path_width
            )

    def get_path(self):
        return self.path
