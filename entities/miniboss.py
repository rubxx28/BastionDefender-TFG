import pygame
from entities.enemy import Enemy


class MiniBoss(Enemy):
    def __init__(self, path, boss_index):
        super().__init__(path)

        self.is_boss = True
        self.boss_index = boss_index

        # -------------------------
        # IMAGEN DEL MINIBOSS (AQUÍ)
        # -------------------------
        boss_image_path = "assets/imagenes/enemies/miniboss.png"

        try:
            base_img = pygame.image.load(boss_image_path).convert_alpha()
        except Exception:
            # fallback si no existe
            base_img = self.base_image

        # Escala visual fuerte
        scale = 1.6 + boss_index * 0.1
        size = int(40 * scale)

        base_img = pygame.transform.smoothscale(base_img, (size, size))

        # Usamos esta imagen como único frame (de momento)
        self.frames = [base_img]
        self.image = self.frames[0]
        self.rect = self.image.get_rect(center=(self.x, self.y))

        # -------------------------
        # STATS ESCALADOS
        # -------------------------
        self.max_hp = int(Enemy.base_hp * (6 + boss_index * 3))
        self.hp = self.max_hp

        self.speed = max(0.25, Enemy.base_speed * (0.65 - boss_index * 0.04))
