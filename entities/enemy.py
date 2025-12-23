import pygame
import math


class Enemy:
    def __init__(self, path):
        self.path = path
        self.index = 0

        # Posición inicial (spawn)
        self.x, self.y = path[0]
        self.speed = 1.2

        # Vida
        self.max_hp = 60
        self.hp = self.max_hp

        # Estados
        self.alive = True
        self.reached_goal = False

        # Imagen
        self.image = pygame.image.load(
            "assets/imagenes/enemies/enemie1Basic.png"
        ).convert_alpha()

        self.image = pygame.transform.scale(self.image, (48, 48))
        self.rect = self.image.get_rect(center=(self.x, self.y))

    def take_damage(self, damage):
        self.hp -= damage
        if self.hp <= 0:
            self.alive = False
            self.reached_goal = False  # 💀 muerto por daño

    def update(self):
        if not self.alive:
            return

        # Seguir el camino
        if self.index < len(self.path) - 1:
            tx, ty = self.path[self.index + 1]
            dx = tx - self.x
            dy = ty - self.y
            dist = math.hypot(dx, dy)

            if dist < self.speed:
                self.index += 1
            else:
                self.x += dx / dist * self.speed
                self.y += dy / dist * self.speed

            self.rect.center = (self.x, self.y)

        else:
            # 🚪 Llegó a la puerta
            self.alive = False
            self.reached_goal = True

    def draw(self, screen):
        screen.blit(self.image, self.rect)

        # Barra de vida
        bar_width = 40
        health_ratio = self.hp / self.max_hp

        pygame.draw.rect(
            screen,
            (60, 60, 60),
            (self.x - bar_width // 2, self.y - 30, bar_width, 5)
        )

        pygame.draw.rect(
            screen,
            (200, 0, 0),
            (self.x - bar_width // 2, self.y - 30, bar_width * health_ratio, 5)
        )
