import pygame
import math
import os


class Enemy:
    # =========================
    # VARIABLES GLOBALES (ESCALADO)
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

        # slowdown state
        self.slow_timer = 0
        self.slow_factor = 1.0  # multiplier applied to self.speed while slowed

        # IMAGEN BASE
        base_path = "assets/imagenes/enemies/enemie1Basic.png"
        try:
            self.base_image = pygame.image.load(base_path).convert_alpha()
            self.base_image = pygame.transform.scale(self.base_image, (40, 40))
        except Exception:
            # fallback if assets missing
            surf = pygame.Surface((40, 40), pygame.SRCALPHA)
            pygame.draw.circle(surf, (180, 100, 100), (20, 20), 18)
            self.base_image = surf

        # FRAMES de animación (buscar secuencia)
        self.frames = []
        base_dir = "assets/imagenes/enemies"
        names_to_try = ["enemie1", "enemie1Basic", "enemie1_walk", "enemy1"]
        for name in names_to_try:
            found = False
            for i in range(1, 6):
                p = os.path.join(base_dir, f"{name}_{i}.png")
                if os.path.exists(p):
                    try:
                        img = pygame.image.load(p).convert_alpha()
                        img = pygame.transform.scale(img, (40, 40))
                        self.frames.append(img)
                        found = True
                    except Exception:
                        pass
            if found:
                break

        if not self.frames:
            self.frames = [self.base_image]

        self.frame_index = 0
        self.frame_timer = 0.0

        self.image = self.frames[0]
        self.rect = self.image.get_rect(center=(self.x, self.y))

        # ANIMACIÓN DE CORRER
        self.anim_phase = 0.0
        self.flip = False

        # Partículas de polvo al pisar
        self.dusts = []

    # DAÑO
    def take_damage(self, damage):
        self.hp -= damage
        if self.hp <= 0:
            self.alive = False
            self.reached_goal = False  # muerto por daño

    # Aplicar ralentización: factor (0.0..1.0) y duración en frames
    def apply_slow(self, factor, duration):
        # Aplicar el factor si es más fuerte (menor) o renovar duración
        if factor < self.slow_factor or duration > self.slow_timer:
            self.slow_factor = factor
            self.slow_timer = duration

    # UPDATE
    def update(self):
        if not self.alive:
            return

        # decrementar slow timer
        if self.slow_timer > 0:
            self.slow_timer -= 1
            if self.slow_timer <= 0:
                self.slow_factor = 1.0

        moved = False
        if self.index < len(self.path) - 1:
            tx, ty = self.path[self.index + 1]
            dx = tx - self.x
            dy = ty - self.y
            dist = math.hypot(dx, dy)

            # usar velocidad efectiva (teniendo en cuenta slow_factor)
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

        rhythm = max(0.8, self.speed * 5.0)
        self.frame_timer += rhythm * 0.08
        if self.frame_timer >= 1.0:
            steps = int(self.frame_timer)
            prev_index = self.frame_index
            self.frame_index = (self.frame_index + steps) % len(self.frames)
            self.frame_timer -= steps

            if moved and self.frame_index != prev_index:
                foot_x = self.x
                foot_y = self.y + self.rect.height // 2 - 6
                self.dusts.append({
                    "x": foot_x + (-4 if self.flip else 4),
                    "y": foot_y,
                    "life": 18,
                    "vy": -0.4,
                    "alpha": 180
                })

        self.anim_phase += rhythm * 0.15
        sway = math.sin(self.anim_phase)
        x_offset = sway * 2
        y_bounce = abs(sway) * 3
        rotation = sway * 5

        img = self.frames[self.frame_index]
        img = pygame.transform.rotate(img, rotation)
        if self.flip:
            img = pygame.transform.flip(img, True, False)

        self.image = img
        self.rect = self.image.get_rect(center=(self.x + x_offset, self.y - y_bounce))

        for d in self.dusts[:]:
            d["x"] += 0
            d["y"] += d["vy"]
            d["vy"] -= 0.02
            d["life"] -= 1
            d["alpha"] = max(0, d["alpha"] - (255 / 18))
            if d["life"] <= 0:
                self.dusts.remove(d)

    # DIBUJO
    def draw(self, screen):
        shadow_w = 36
        shadow_h = 12
        shadow_surf = pygame.Surface((shadow_w, shadow_h), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow_surf, (0, 0, 0, 120), (0, 0, shadow_w, shadow_h))
        shadow_pos = (self.x - shadow_w // 2, self.y + self.rect.height // 2 - 6)
        screen.blit(shadow_surf, shadow_pos)

        # indicador visual si está ralentizado
        if self.slow_timer > 0:
            r = max(self.rect.width // 2 + 2, 18)
            s = pygame.Surface((r*2, r*2), pygame.SRCALPHA)
            pygame.draw.circle(s, (60, 140, 220, 90), (r, r), r)
            screen.blit(s, (self.x - r, self.y - r))

        for d in self.dusts:
            surf = pygame.Surface((8, 8), pygame.SRCALPHA)
            a = int(max(0, d.get("alpha", 120)))
            pygame.draw.circle(surf, (120, 100, 80, a), (4, 4), 4)
            screen.blit(surf, (d["x"] - 4, d["y"] - 4))

        screen.blit(self.image, self.rect)

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