import pygame
import math

class Enemy:
    def __init__(self, path):
        self.path = path
        self.current_point = 0

        self.x, self.y = self.path[0]
        self.speed = 2
        self.radius = 12

        self.health = 100
        self.alive = True

    def update(self):
        if self.current_point >= len(self.path) - 1:
            self.alive = False
            return

        target_x, target_y = self.path[self.current_point + 1]

        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.hypot(dx, dy)

        if distance < self.speed:
            self.current_point += 1
        else:
            self.x += dx / distance * self.speed
            self.y += dy / distance * self.speed

    def draw(self, screen):
        pygame.draw.circle(
            screen,
            (150, 0, 0),  # rojo oscuro medieval
            (int(self.x), int(self.y)),
            self.radius
        )
