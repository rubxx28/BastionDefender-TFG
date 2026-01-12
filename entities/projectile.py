import pygame
import math
from settings import FPS


class Arrow:
    def __init__(self, pos, target, damage):
        self.x, self.y = pos
        self.target = target
        self.damage = damage
        self.speed = 6
        self.alive = True

        self.base_image = pygame.image.load("assets/imagenes/projectiles/bolaMosqueteros.png").convert_alpha()
        self.base_image = pygame.transform.scale(self.base_image, (45, 25))
        self.image = self.base_image
        self.rect = self.image.get_rect(center=pos)

        self.trail = []  # list of (x,y,life)

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

        vx = dx / dist * self.speed
        vy = dy / dist * self.speed
        self.x += vx
        self.y += vy
        self.rect.center = (self.x, self.y)

        # append to trail
        self.trail.append({"x": self.x, "y": self.y, "life": 12})
        if len(self.trail) > 12:
            self.trail.pop(0)

    def draw(self, screen):
        # draw trail (fading)
        for i, t in enumerate(self.trail):
            a = int(200 * (i / max(1, len(self.trail))))
            surf = pygame.Surface((6, 6), pygame.SRCALPHA)
            pygame.draw.circle(surf, (240, 220, 120, a), (3, 3), 3)
            screen.blit(surf, (t["x"] - 3, t["y"] - 3))

        # rotate to face movement direction
        if self.target:
            dx = self.target.x - self.x
            dy = self.target.y - self.y
            angle = math.degrees(math.atan2(-dy, dx))  # negative dy because pygame y-axis
            rotated = pygame.transform.rotate(self.base_image, angle)
            rect = rotated.get_rect(center=(self.x, self.y))
            screen.blit(rotated, rect)
        else:
            screen.blit(self.image, self.rect)


class CannonBall:
    def __init__(self, pos, target, damage, enemies=None, aoe_radius=60):
        self.x, self.y = pos
        self.target = target
        self.damage = damage
        self.speed = 4
        self.alive = True

        self.image = pygame.image.load("assets/imagenes/projectiles/bolaMosqueteros.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (36, 36))
        self.rect = self.image.get_rect(center=pos)

        self.trail = []
        self.enemies = enemies  # referencia a la lista global de enemigos (para AoE)
        self.aoe_radius = aoe_radius

    def update(self):
        # si el target muere antes, seguir hacia su última posición no es viable → eliminar
        if not self.target.alive and not self.enemies:
            self.alive = False
            return

        dx = self.target.x - self.x
        dy = self.target.y - self.y
        dist = math.hypot(dx, dy)

        if dist < self.speed:
            # Impacto: aplicar daño en área si tenemos lista de enemigos
            if self.enemies:
                for e in self.enemies:
                    if e.alive:
                        d = math.hypot(e.x - self.x, e.y - self.y)
                        if d <= self.aoe_radius:
                            e.take_damage(self.damage)
            else:
                self.target.take_damage(self.damage)
            self.alive = False
            return

        self.x += dx / dist * self.speed
        self.y += dy / dist * self.speed
        self.rect.center = (self.x, self.y)

        # smoke trail
        self.trail.append({"x": self.x, "y": self.y, "life": 18})
        if len(self.trail) > 10:
            self.trail.pop(0)

    def draw(self, screen):
        # draw smoke
        for i, t in enumerate(self.trail):
            a = int(120 * (i / max(1, len(self.trail))))
            surf = pygame.Surface((12, 12), pygame.SRCALPHA)
            pygame.draw.circle(surf, (100, 90, 80, a), (6, 6), 6)
            screen.blit(surf, (t["x"] - 6, t["y"] - 6))

        screen.blit(self.image, self.rect)


class MagicMissile:
    def __init__(self, pos, target, damage):
        self.x, self.y = pos
        self.target = target
        self.damage = damage
        self.speed = 5
        self.alive = True

        self.base_image = pygame.image.load("assets/imagenes/projectiles/orbeMagico.png").convert_alpha()
        self.base_image = pygame.transform.scale(self.base_image, (40, 40))
        self.image = self.base_image
        self.rect = self.image.get_rect(center=pos)

        self.trail = []

    def update(self):
        if not self.target.alive:
            self.alive = False
            return

        dx = self.target.x - self.x
        dy = self.target.y - self.y
        dist = math.hypot(dx, dy)

        if dist < self.speed:
            # Daño + slow
            self.target.take_damage(self.damage)
            # aplicar slow: 0.5x speed por ~1.8s
            try:
                self.target.apply_slow(0.5, int(FPS * 1.8))
            except Exception:
                pass
            self.alive = False
            return

        self.x += dx / dist * self.speed
        self.y += dy / dist * self.speed
        self.rect.center = (self.x, self.y)

        # glowing trail
        self.trail.append({"x": self.x, "y": self.y, "life": 14})
        if len(self.trail) > 14:
            self.trail.pop(0)

    def draw(self, screen):
        # draw glow trail
        for i, t in enumerate(self.trail):
            a = int(160 * (i / max(1, len(self.trail))))
            surf = pygame.Surface((8, 8), pygame.SRCALPHA)
            pygame.draw.circle(surf, (180, 150, 255, a), (4, 4), 4)
            screen.blit(surf, (t["x"] - 4, t["y"] - 4))

        screen.blit(self.image, self.rect)