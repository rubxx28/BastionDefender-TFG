import pygame
import math

class Enemy:
    def __init__(self, path):
        self.path = path
        self.index = 0

        self.x, self.y = self.path[0]
        self.speed = 2.2
        self.alive = True

        self.image_base = pygame.image.load(
            "assets/imagenes/enemies/enemie1Basic.png"
        ).convert_alpha()

        self.image_base = pygame.transform.scale(self.image_base, (32, 32))
        self.image = self.image_base
        self.rect = self.image.get_rect(center=(self.x, self.y))

        # Animación
        self.walk_phase = 0

    def update(self):
        if self.index >= len(self.path) - 1:
            self.alive = False
            return

        tx, ty = self.path[self.index + 1]
        dx = tx - self.x
        dy = ty - self.y
        dist = math.hypot(dx, dy)

        if dist < self.speed:
            self.index += 1
        else:
            self.x += dx / dist * self.speed
            self.y += dy / dist * self.speed

        # Orientación
        if dx < 0:
            self.image = pygame.transform.flip(self.image_base, True, False)
        else:
            self.image = self.image_base

        # Animación de caminar (muy visible)
        self.walk_phase += 0.25
        y_offset = math.sin(self.walk_phase) * 4

        self.rect.center = (self.x, self.y + y_offset)

    def draw(self, screen):
        screen.blit(self.image, self.rect)
