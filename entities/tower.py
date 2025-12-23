import pygame
import math
from entities.projectile import Arrow


class Tower:
    def __init__(self, pos):
        self.x, self.y = pos
        self.level = 1

        self.range = 140
        self.fire_rate = 60
        self.damage = 20
        self.cooldown = 0

        self.image = pygame.image.load(
            "assets/imagenes/towers/torreArqueras1.png"
        ).convert_alpha()

        self.image = pygame.transform.scale(self.image, (80, 80))
        self.rect = self.image.get_rect(center=pos)

    def upgrade(self):
        self.level += 1
        self.range += 40
        self.damage += 15
        self.fire_rate = max(30, self.fire_rate - 15)

        self.image = pygame.image.load(
            "assets/imagenes/towers/torreArqueras3.png"
        ).convert_alpha()
        self.image = pygame.transform.scale(self.image, (90, 90))
        self.rect = self.image.get_rect(center=(self.x, self.y))

    def update(self, enemies, projectiles):
        if self.cooldown > 0:
            self.cooldown -= 1
            return

        for enemy in enemies:
            dist = math.hypot(enemy.x - self.x, enemy.y - self.y)
            if dist <= self.range:
                projectiles.append(
                    Arrow((self.x, self.y), enemy)
                )
                self.cooldown = self.fire_rate
                break

    def draw(self, screen):
        screen.blit(self.image, self.rect)
