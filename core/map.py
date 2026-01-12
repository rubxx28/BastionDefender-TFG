import pygame
import random
from settings import WIDTH, HEIGHT


class GameMap:
    def __init__(self):
        # -------------------------
        # Cargar y escalar mapa
        # -------------------------
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

        # -------------------------
        # PATH IZQUIERDO
        # -------------------------
        self.path_left = [
            (520, 110),
            (520, 144),
            (524, 163),
            (532, 182),
            (541, 201),
            (540, 222),
            (532, 242),
            (514, 261),
            (502, 280),
            (487, 301),
            (494, 320),
            (506, 336),
            (527, 357),
            (543, 377),
            (565, 401),
            (578, 425),
            (595, 455),
            (613, 476),
            (633, 499),
            (639, 517)
        ]

        # -------------------------
        # PATH DERECHO
        # -------------------------
        self.path_right = [
            (760, 110),
            (758, 139),
            (763, 159),
            (773, 181),
            (786, 207),
            (792, 230),
            (790, 252),
            (774, 274),
            (754, 300),
            (743, 318),
            (742, 349),
            (754, 370),
            (770, 402),
            (770, 427),
            (749, 449),
            (713, 466),
            (682, 482),
            (651, 495),
            (641, 516)
        ]

        # -------------------------
        # ZONAS PARA TORRES
        # -------------------------
        self.tower_spots = [
            (450, 260),
            (580, 320),
            (700, 350),
            (840, 260),
            (520, 430),
            (660, 420),
            (830, 430),
            (720, 250)
        ]

    def draw(self, screen):
        screen.fill((0, 0, 0))
        screen.blit(self.background, (self.bg_x, 0))

    def draw_tower_spots(self, screen, occupied_spots):
        for spot in self.tower_spots:
            if spot not in occupied_spots:
                pygame.draw.circle(screen, (180, 180, 100), spot, 30, 2)

    def get_path(self):
        return random.choice([self.path_left, self.path_right])
