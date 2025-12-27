import pygame
import math


class Enemy:
    # =========================
    # VARIABLES GLOBALES (ESCALADO)
    # =========================
    base_speed = 0.55
    base_hp = 60

    def __init__(self, path):
        # -------------------------
        # PATH
        # -------------------------
        self.path = path
        self.index = 0

        # -------------------------
        # POSICIÓN
        # -------------------------
        self.x, self.y = path[0]
        self.speed = Enemy.base_speed

        # -------------------------
        # VIDA
        # -------------------------
        self.max_hp = Enemy.base_hp
        self.hp = self.max_hp

        # -------------------------
        # ESTADOS
        # -------------------------
        self.alive = True
        self.reached_goal = False

        # -------------------------
        # IMAGEN BASE
        # -------------------------
        self.base_image = pygame.image.load(
            "assets/imagenes/enemies/enemie1Basic.png"
        ).convert_alpha()

        self.base_image = pygame.transform.scale(self.base_image, (40, 40))
        self.image = self.base_image
        self.rect = self.image.get_rect(center=(self.x, self.y))

        # -------------------------
        # ANIMACIÓN DE CORRER
        # -------------------------
        self.anim_phase = 0.0
        self.flip = False

    # -------------------------
    # DAÑO
    # -------------------------
    def take_damage(self, damage):
        self.hp -= damage
        if self.hp <= 0:
            self.alive = False
            self.reached_goal = False  # 💀 muerto por daño

    # -------------------------
    # UPDATE
    # -------------------------
    def update(self):
        if not self.alive:
            return

        # =========================
        # MOVIMIENTO POR EL CAMINO
        # =========================
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

            # Dirección horizontal
            self.flip = dx < 0
        else:
            # 🚪 LLEGÓ A LA PUERTA
            self.alive = False
            self.reached_goal = True
            return

        # =========================
        # ANIMACIÓN DE CORRER
        # =========================
        self.anim_phase += 0.25

        sway = math.sin(self.anim_phase)
        x_offset = sway * 2            # paso lateral
        y_bounce = abs(sway) * 3       # rebote al pisar
        rotation = sway * 5            # balanceo del cuerpo

        img = pygame.transform.rotate(self.base_image, rotation)
        if self.flip:
            img = pygame.transform.flip(img, True, False)

        self.image = img
        self.rect = self.image.get_rect(
            center=(self.x + x_offset, self.y - y_bounce)
        )

    # -------------------------
    # DIBUJO
    # -------------------------
    def draw(self, screen):
        screen.blit(self.image, self.rect)

        # Barra de vida
        bar_width = 40
        ratio = max(0, self.hp / self.max_hp)

        pygame.draw.rect(
            screen,
            (60, 60, 60),
            (self.x - bar_width // 2, self.y - 30, bar_width, 5)
        )
        pygame.draw.rect(
            screen,
            (200, 0, 0),
            (self.x - bar_width // 2, self.y - 30, bar_width * ratio, 5)
        )
