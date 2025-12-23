import pygame
import math


class Arrow:
    def __init__(self, pos, target):
        self.x, self.y = pos
        self.target = target
        self.speed = 6
        self.damage = 20
        self.alive = True

        self.image = pygame.image.load(
            "assets/imagenes/arrows/flecha3.png"
        ).convert_alpha()

        self.image = pygame.transform.scale(self.image, (56, 18))
        self.rect = self.image.get_rect(center=pos)

    def update(self):
        if not self.target.alive:
            self.alive = False
            return

        dx = self.target.x - self.x
        dy = self.target.y - self.y
        dist = math.hypot(dx, dy)

        if dist < self.speed:
            self.target.take_damage(self.damage)
            self.alive = False
            return

        dx /= dist
        dy /= dist

        self.x += dx * self.speed
        self.y += dy * self.speed
        self.rect.center = (self.x, self.y)

    def draw(self, screen):
        screen.blit(self.image, self.rect)
