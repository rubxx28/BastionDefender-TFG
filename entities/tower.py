import pygame
import math
from entities.projectile import Arrow, CannonBall


# =========================
# TORRE BASE
# =========================
class BaseTower:
    def __init__(self, x, y):
        self.x = x
        self.y = y

        self.level = 1
        self.max_level = 3
        self.range = 140
        self.damage = 20
        self.fire_rate = 60
        self.cooldown = 0

        self.images = {}
        self.image = None
        self.rect = None

    def update(self, enemies, projectiles):
        if self.cooldown > 0:
            self.cooldown -= 1
            return

        for enemy in enemies:
            dist = math.hypot(enemy.x - self.x, enemy.y - self.y)
            if dist <= self.range:
                self.shoot(enemy, projectiles)
                self.cooldown = self.fire_rate
                break

    def shoot(self, enemy, projectiles):
        pass

    def upgrade(self):
        if self.level >= self.max_level:
            return False
        
        self.level += 1
        self.damage += 15
        self.fire_rate = max(20, self.fire_rate - 10)
        self.load_image()   # 🔥 CLAVE: recargar imagen
        return True
    
    def draw(self, screen):
        screen.blit(self.image, self.rect)


# =========================
# TORRE DE MOSQUETEROS
# =========================
class MusketeerTower(BaseTower):
    def __init__(self, x, y):
        super().__init__(x, y)

        self.images = {
            1: "assets/imagenes/towers/mosquetera1.png",
            2: "assets/imagenes/towers/mosquetera2.png",
            3: "assets/imagenes/towers/mosquetera3.png",
        }

        self.load_image()

    def load_image(self):
        sizes = {
            1: (100, 100),
            2: (100, 100),
            3: (100, 110),
        }

        img = pygame.image.load(self.images[self.level]).convert_alpha()
        self.image = pygame.transform.smoothscale(img, sizes[self.level])
        self.rect = self.image.get_rect(center=(self.x, self.y))

    def shoot(self, enemy, projectiles):
        projectiles.append(
            Arrow((self.x, self.y), enemy, self.damage)
        )


# =========================
# TORRE CAÑÓN
# =========================
class CannonTower(BaseTower):
    def __init__(self, x, y):
        super().__init__(x, y)

        self.range = 170
        self.damage = 35
        self.fire_rate = 90

        self.images = {
            1: "assets/imagenes/towers/cañon1.png",
            2: "assets/imagenes/towers/cañon2.png",
            3: "assets/imagenes/towers/cañon3.png",
        }

        self.load_image()

    def load_image(self):
        sizes = {
            1: (80, 280),
            2: (100, 200),
            3: (120, 220),
        }

        img = pygame.image.load(self.images[self.level]).convert_alpha()
        self.image = pygame.transform.smoothscale(img, sizes[self.level])
        self.rect = self.image.get_rect(center=(self.x, self.y))

    def shoot(self, enemy, projectiles):
        projectiles.append(
            CannonBall((self.x, self.y), enemy, self.damage)
        )
