import pygame
import math
import os


class Enemy:
    # =========================
    # VARIABLES GLOBALES
    # =========================
    base_speed = 0.55
    base_hp = 60

    def __init__(self, path):
        # PATH
        self.path = path
        self.index = 0

        # POSICIÓN
        self.x, self.y = path[0]
        self.speed = Enemy.base_speed

        # VIDA
        self.max_hp = Enemy.base_hp
        self.hp = self.max_hp

        # ESTADOS
        self.alive = True
        self.reached_goal = False

        # SLOW / MAGIA
        self.slow_timer = 0
        self.slow_factor = 1.0
        self.magic_aura_timer = 0

        # -------------------------
        # IMAGEN BASE (NO TOCAR ASSETS)
        # -------------------------
        base_path = "assets/imagenes/enemies/enemigo.png"
        try:
            self.base_image = pygame.image.load(base_path).convert_alpha()
            self.base_image = pygame.transform.scale(self.base_image, (60, 60))
        except Exception:
            surf = pygame.Surface((40, 40), pygame.SRCALPHA)
            pygame.draw.circle(surf, (180, 100, 100), (20, 20), 18)
            self.base_image = surf

        # -------------------------
        # FRAMES DE ANIMACIÓN
        # -------------------------
        self.frames = []
        base_dir = "assets/imagenes/enemies"
        names_to_try = ["enemie1", "enemie1Basic", "enemie1_walk", "enemy1"]

        for name in names_to_try:
            found = False
            for i in range(1, 6):
                p = os.path.join(base_dir, f"{name}_{i}.png")
                if os.path.exists(p):
                    img = pygame.image.load(p).convert_alpha()
                    img = pygame.transform.scale(img, (40, 40))
                    self.frames.append(img)
                    found = True
            if found:
                break

        if not self.frames:
            self.frames = [self.base_image]

        self.frame_index = 0
        self.frame_timer = 0.0

        self.image = self.frames[0]
        self.rect = self.image.get_rect(center=(self.x, self.y))

        # ANIMACIÓN
        self.anim_phase = 0.0
        self.flip = False

        # POLVO
        self.dusts = []

    # =========================
    # COMBATE
    # =========================
    def take_damage(self, damage):
        self.hp -= damage
        if self.hp <= 0:
            self.alive = False
            self.reached_goal = False

    def apply_slow(self, factor, duration):
        if factor < self.slow_factor or duration > self.slow_timer:
            self.slow_factor = factor
            self.slow_timer = duration
            self.magic_aura_timer = duration

    # =========================
    # UPDATE
    # =========================
    def update(self):
        if not self.alive:
            return

        # Slow
        if self.slow_timer > 0:
            self.slow_timer -= 1
            if self.slow_timer <= 0:
                self.slow_factor = 1.0

        if self.magic_aura_timer > 0:
            self.magic_aura_timer -= 1

        moved = False

        # Movimiento por el camino
        if self.index < len(self.path) - 1:
            tx, ty = self.path[self.index + 1]
            dx = tx - self.x
            dy = ty - self.y
            dist = math.hypot(dx, dy)

            eff_speed = self.speed * self.slow_factor

            if dist < eff_speed:
                self.index += 1
            else:
                self.x += dx / dist * eff_speed
                self.y += dy / dist * eff_speed
                moved = True

            self.flip = dx < 0
        else:
            self.alive = False
            self.reached_goal = True
            return

        # -------------------------
        # ANIMACIÓN DE LEVITACIÓN
        # -------------------------
        self.anim_phase += self.speed * 0.35
        sway2 = math.sin(self.anim_phase * 0.3)  # oscilación muy lenta para levitación suave

        self.frame_timer += 0.12
        if self.frame_timer >= 1:
            self.frame_index = (self.frame_index + 1) % len(self.frames)
            self.frame_timer = 0

        img = self.frames[self.frame_index]
        
        # Sin rotación - animación muy sutil
        img = pygame.transform.rotate(img, sway2 * 1)

        if self.flip:
            img = pygame.transform.flip(img, True, False)

        self.image = img
        
        # 🔥 LEVITACIÓN SUTIL: Solo movimiento vertical muy suave
        levitate_y = abs(sway2) * 4  # Flota muy poco hacia arriba y abajo
        
        self.rect = self.image.get_rect(center=(self.x, self.y - levitate_y))

        # Polvo al moverse
        if moved and int(self.anim_phase * 10) % 6 == 0:
            self.dusts.append({
                "x": self.x,
                "y": self.y + self.rect.height // 2 - 4,
                "life": 14,
                "alpha": 140
            })

        for d in self.dusts[:]:
            d["life"] -= 1
            d["alpha"] -= 10
            if d["life"] <= 0:
                self.dusts.remove(d)

    # =========================
    # DRAW
    # =========================
    def draw(self, screen):
        # Sombra en el suelo
        shadow = pygame.Surface((36, 10), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow, (0, 0, 0, 130), (0, 0, 36, 10))
        screen.blit(shadow, (self.x - 18, self.y + self.rect.height // 2 - 4))

        # Aura mágica (slow)
        if self.magic_aura_timer > 0:
            r = max(self.rect.width // 2 + 3, 22)
            alpha = int(150 * (self.magic_aura_timer / max(1, 120)))
            aura = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
            pygame.draw.circle(aura, (100, 150, 255, alpha), (r, r), r)
            screen.blit(aura, (self.x - r, self.y - r))

        # Polvo
        for d in self.dusts:
            surf = pygame.Surface((6, 6), pygame.SRCALPHA)
            pygame.draw.circle(surf, (120, 100, 80, d["alpha"]), (3, 3), 3)
            screen.blit(surf, (d["x"] - 3, d["y"] - 3))

        # Enemigo
        screen.blit(self.image, self.rect)

        # Barra de vida - subida arriba de la cabeza
        ratio = max(0, self.hp / self.max_hp)
        bar_width = 40

        pygame.draw.rect(
            screen, (60, 60, 60),
            (self.x - bar_width // 2, self.y - 48, bar_width, 5)
        )
        pygame.draw.rect(
            screen, (200, 0, 0),
            (self.x - bar_width // 2, self.y - 48, bar_width * ratio, 5)
        )
