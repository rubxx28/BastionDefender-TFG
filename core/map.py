import pygame
import random
from settings import WIDTH, HEIGHT


class GameMap:
    def __init__(self):
        # -------------------------
        # Cargar y escalar mapa
        # -------------------------
        self.background = pygame.image.load(
            "assets/imagenes/mapa/mapa.png"
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
            (160, 90),
            (189, 159),
            (217, 185),
            (410, 210),
            (448, 210),
            (517, 215),
            (578, 231),
            (672, 241),
            (741, 244),
            (787, 250),
            (833, 252),
            (910, 263),
            (949, 279),
            (987, 325),
            (997, 356),
            (984, 393),
            (949, 412),
            (888, 436),
            (811, 457),
            (723, 473),
            (636, 468),
            (574, 447), 
            (496, 416),       
            (426, 388),  
            (360, 377),  
            (304, 375), 
            (221, 389),  
            (171, 433),  
            (174, 474),  
            (236, 542), 
            (337, 564), 
            (443, 578),  
            (535, 586), 
            (638, 600),  
            (750, 621),  
            (870, 648),  
            (980, 649),  
            (1076, 660),  
            (1140, 692),  
            (1206, 710)
            
        ]

        # -------------------------
        # PATH DERECHO
        # -------------------------
        self.path_right = [
            (1122, 81),
            (1110, 121),
            (1095, 161),
            (1083, 204),
            (1087, 251),
            (1036, 283),
            (990,  293),
            (999, 342),
            (984, 393),
            (949, 412),
            (888, 436),
            (811, 457),
            (723, 473),
            (636, 468),
            (574, 447), 
            (496, 416),       
            (426, 388),  
            (360, 377),  
            (304, 375), 
            (221, 389),  
            (171, 433),  
            (174, 474),  
            (236, 542), 
            (337, 564), 
            (443, 578),  
            (535, 586), 
            (638, 600),  
            (750, 621),  
            (870, 648),  
            (980, 649),  
            (1076, 660),  
            (1140, 692),  
            (1206, 710),
            ]

        # -------------------------
        # ZONAS PARA TORRES
        # -------------------------
        self.tower_spots = [
            (563, 157),
            (733, 175),
            (874, 191),
            (1001, 214),
            (702, 388),
            (255, 306),
            (678, 542),
            (34, 386),
            (642, 672),
            (1116, 332)
        ]

        # No usar icono por defecto para spots (se pinta un marcador sutil)
        self.spot_icon = None

    def draw(self, screen):
        screen.fill((0, 0, 0))
        screen.blit(self.background, (self.bg_x, 0))


        # Dibujar zonas de torre con icono/base
        for spot in self.tower_spots:
            if spot:
                self._draw_spot(screen, spot, available=True)

    def _draw_spot(self, screen, spot, available=True):
        """Draw a subtle spot marker used for tower placement.
        - Draws a translucent ring (no heavy brown base)
        - Shows range highlight when hovering
        """
        x, y = spot
        mx, my = pygame.mouse.get_pos()
        hover = ((mx - x) ** 2 + (my - y) ** 2) ** 0.5 < 28

        # base: translucent soft circle to blend with grass
        surf = pygame.Surface((64, 64), pygame.SRCALPHA)
        pygame.draw.circle(surf, (220, 200, 140, 30), (32, 32), 20)  # soft fill
        pygame.draw.circle(surf, (220, 200, 140, 160), (32, 32), 20, 2)  # faint outline
        screen.blit(surf, (x - 32, y - 32))

        # small center marker
        pygame.draw.circle(screen, (245, 245, 220), (x, y), 6)
        pygame.draw.circle(screen, (210, 180, 120), (x, y), 6, 1)

        # if hovering, draw range indicator (very subtle)
        if hover:
            rng = 110  # default visualization range
            r_surf = pygame.Surface((rng * 2, rng * 2), pygame.SRCALPHA)
            pygame.draw.circle(r_surf, (255, 255, 200, 30), (rng, rng), rng)
            pygame.draw.circle(r_surf, (255, 255, 200, 80), (rng, rng), rng, 2)
            screen.blit(r_surf, (x - rng, y - rng))

        # if spot occupied, draw a tiny tower-like icon (non-brown) - placeholder rectangle + flag
        if not available:
            pygame.draw.rect(screen, (150, 150, 170), (x - 8, y - 18, 16, 16))
            pygame.draw.polygon(screen, (200, 60, 60), [(x, y - 24), (x + 8, y - 16), (x, y - 16)])

    def draw_tower_spots(self, screen, occupied_spots):
        for spot in self.tower_spots:
            if spot not in occupied_spots:
                self._draw_spot(screen, spot, available=True)


    def get_path(self):
        return random.choice([self.path_left, self.path_right])
