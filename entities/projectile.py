import pygame
import math


class Arrow:
    def __init__(self, pos, target, damage):
        self.x, self.y = pos
        self.target = target
        self.damage = damage
        self.speed = 6
        self.alive = True

        self.image = pygame.image.load(
            "assets/imagenes/projectiles/bolaMosqueteros.png"
        ).convert_alpha()

        self.image = pygame.transform.scale(self.image, (45, 25))
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

        self.x += dx / dist * self.speed
        self.y += dy / dist * self.speed
        self.rect.center = (self.x, self.y)

    def draw(self, screen):
        screen.blit(self.image, self.rect)


class CannonBall:
    def __init__(self, pos, target, damage):
        self.x, self.y = pos
        self.target = target
        self.damage = damage
        self.speed = 4
        self.alive = True

        self.image = pygame.image.load(
            "assets/imagenes/projectiles/bolaCañon1.png"
        ).convert_alpha()

        self.image = pygame.transform.scale(self.image, (130, 130))
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

        self.x += dx / dist * self.speed
        self.y += dy / dist * self.speed
        self.rect.center = (self.x, self.y)

    def draw(self, screen):
        screen.blit(self.image, self.rect)
