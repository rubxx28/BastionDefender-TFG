import pygame
import random
from settings import WIDTH, HEIGHT

class GameMap:
    def __init__(self):
        self.background = pygame.image.load(
            "assets/imagenes/mapa/mapa_principal.png"
        ).convert()

        map_w, map_h = self.background.get_size()
        scale = HEIGHT / map_h
        self.map_width = int(map_w * scale)

        self.background = pygame.transform.smoothscale(
            self.background, (self.map_width, HEIGHT)
        )

        self.bg_x = (WIDTH - self.map_width) // 2

        # ===============================
        # SPAWNS (luces azules)
        # ===============================
        self.spawn_left = (
            self.bg_x + int(self.map_width * 0.27),
            int(HEIGHT * 0.10)
        )

        self.spawn_right = (
            self.bg_x + int(self.map_width * 0.73),
            int(HEIGHT * 0.10)
        )

        # ===============================
        # PUERTA MEDIEVAL
        # ===============================
        self.gate = (
            self.bg_x + self.map_width // 2,
            int(HEIGHT * 0.78)
        )

        # ===============================
        # PATHS (siguen el camino real)
        # ===============================
        self.path_left = [
            self.spawn_left,
            (self.bg_x + int(self.map_width * 0.30), int(HEIGHT * 0.30)),
            (self.bg_x + int(self.map_width * 0.40), int(HEIGHT * 0.55)),
            self.gate
        ]

        self.path_right = [
            self.spawn_right,
            (self.bg_x + int(self.map_width * 0.70), int(HEIGHT * 0.30)),
            (self.bg_x + int(self.map_width * 0.60), int(HEIGHT * 0.55)),
            self.gate
        ]

    def draw(self, screen):
        screen.fill((0, 0, 0))
        screen.blit(self.background, (self.bg_x, 0))

    def get_path(self):
        return random.choice([self.path_left, self.path_right])
