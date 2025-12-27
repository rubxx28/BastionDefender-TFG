import pygame
import math
from entities.projectile import CannonBall


class Cannon:
    def __init__(self, pos):
        self.x, self.y = pos
        self.type = "cannon"
        self.level = 1

        self.range = 120
        self.fire_rate = 90
        self.damage = 50
        self.cooldown = 0

        self.image = pygame.image.load(
            "assets/imagenes/towers/cañon1.png"
        ).convert_alpha()

        self.image = pygame.transform.scale(self.image, (90, 90))
        self.rect = self.image.get_rect(center=pos)

    def upgrade(self):
        self.level += 1
        self.damage += 30
        self.fire_rate = max(60, self.fire_rate - 10)

        self.image = pygame.image.load(
            "assets/imagenes/towers/cañon2.png"
        ).convert_alpha()
        self.image = pygame.transform.scale(self.image, (100, 100))
        self.rect = self.image.get_rect(center=(self.x, self.y))

    def update(self, enemies, projectiles):
        if self.cooldown > 0:
            self.cooldown -= 1
            return

        for enemy in enemies:
            dist = math.hypot(enemy.x - self.x, enemy.y - self.y)
            if dist <= self.range:
                projectiles.append(
                    CannonBall((self.x, self.y), enemy, self.damage)
                )
                self.cooldown = self.fire_rate
                break

    def draw(self, screen):
        screen.blit(self.image, self.rect)
