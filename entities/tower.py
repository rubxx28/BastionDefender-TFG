import pygame
import math
import random
from entities.projectile import Arrow, CannonBall, MagicMissile

# =========================
# TORRE BASE
# =========================
class BaseTower:
    def __init__(self, x, y):
        # Posición centrada EXACTA
        self.x = int(x)
        self.y = int(y)

        self.level = 1
        self.max_level = 3

        self.range = 140
        self.damage = 20
        self.fire_rate = 60
        self.fire_timer = 0

        self.target = None

        # Orientación
        self.facing_left = False

        # Animación disparo / muzzle
        self.recoil = 0
        self.recoil_speed = 0.2
        self.muzzle_timer = 0
        self.muzzle_duration = 10
        self.muzzle_particles = []  # partículas (chispa + humo)

        # Animación de mejora
        self.upgrade_anim_timer = 0
        self.upgrade_anim_duration = 60  # frames
        self.level_label_timer = 0
        self.level_label_duration = 60

        # Fuente para texto de nivel
        self.level_font = pygame.font.SysFont("arial", 14)

        # Cost tracking
        self.upgrade_cost = 75
        self.cost = 0
        self.total_cost = 0

    # -------------------------
    # BUSCAR OBJETIVO
    # -------------------------
    def find_target(self, enemies):
        self.target = None
        for enemy in enemies:
            dist = math.hypot(enemy.x - self.x, enemy.y - self.y)
            if dist <= self.range:
                self.target = enemy
                return

    # -------------------------
    # SPAWN MUZZLE PARTICLES
    # -------------------------
    def _spawn_muzzle(self, direction_angle):
        # barrel tip
        barrel_dist = 36
        tip_x = self.x + math.cos(direction_angle) * barrel_dist
        tip_y = self.y + math.sin(direction_angle) * barrel_dist - 6

        # bright spark particles
        for _ in range(3):
            ang = direction_angle + random.uniform(-0.6, 0.6)
            speed = random.uniform(1.6, 3.0)
            self.muzzle_particles.append({
                "x": tip_x,
                "y": tip_y,
                "vx": math.cos(ang) * speed,
                "vy": math.sin(ang) * speed - 0.6,
                "life": random.randint(10, 16),
                "size": random.randint(2, 4),
                "color": (255, 220, 120),
                "alpha": 255
            })
        # smoke puffs
        for _ in range(2):
            self.muzzle_particles.append({
                "x": tip_x + random.uniform(-6, 6),
                "y": tip_y + random.uniform(-4, 4),
                "vx": random.uniform(-0.4, 0.4),
                "vy": random.uniform(-0.8, -0.4),
                "life": random.randint(24, 40),
                "size": random.randint(6, 12),
                "color": (120, 110, 100),
                "alpha": 180
            })

        self.muzzle_timer = self.muzzle_duration
        # recoil bump
        self.recoil = 1.6

    # -------------------------
    # UPDATE
    # -------------------------
    def update(self, enemies, projectiles):
        self.fire_timer += 1
        self.find_target(enemies)

        # Recoil vuelve a su sitio
        if self.recoil > 0:
            self.recoil -= self.recoil_speed
            if self.recoil < 0:
                self.recoil = 0

        # Muzzle particles update
        for p in self.muzzle_particles[:]:
            p["x"] += p["vx"]
            p["y"] += p["vy"]
            p["vy"] += 0.06  # gravedad ligera
            p["life"] -= 1
            p["alpha"] = max(0, p["alpha"] - int(255 / (p.get("life", 1) + 1)))
            if p["life"] <= 0:
                self.muzzle_particles.remove(p)

        # Decrementar animaciones
        if self.muzzle_timer > 0:
            self.muzzle_timer -= 1
        if self.upgrade_anim_timer > 0:
            self.upgrade_anim_timer -= 1
        if self.level_label_timer > 0:
            self.level_label_timer -= 1

        if self.target and self.fire_timer >= self.fire_rate:
            # Orientación hacia el enemigo
            self.facing_left = self.target.x < self.x

            # angle to target
            dx = self.target.x - self.x
            dy = self.target.y - self.y
            angle = math.atan2(dy, dx)

            # spawn projectile (subclases) and muzzle effects
            # ahora PASAMOS 'enemies' para que ciertos proyectiles (AoE/efectos) puedan usarlos
            self.shoot(self.target, projectiles, enemies)
            self._spawn_muzzle(angle)

            self.fire_timer = 0
            self.recoil = 1.6  # animación disparo

    # -------------------------
    # UPGRADE
    # -------------------------
    def upgrade(self):
        if self.level >= self.max_level:
            return False

        self.level += 1
        self.damage += 15
        self.range += 20
        self.fire_rate = max(25, self.fire_rate - 10)

        # registrar coste de la mejora
        self.total_cost += self.upgrade_cost

        self.load_image()

        # Iniciar animaciones de mejora
        self.upgrade_anim_timer = self.upgrade_anim_duration
        self.level_label_timer = self.level_label_duration

        return True

    def sell_refund(self):
        return int(self.total_cost / 2)

    # -------------------------
    # DIBUJO
    # -------------------------
    def draw(self, screen):
        img = self.image

        # Flip horizontal if necessary
        if self.facing_left:
            img = pygame.transform.flip(img, True, False)

        # Recoil visual (retroceso)
        offset_x = -6 if self.recoil > 0 and not self.facing_left else 6 if self.recoil > 0 else 0
        if self.facing_left:
            offset_x *= -1

        rect = img.get_rect(center=(self.x + offset_x, self.y))

        # --- RESTAURADO: destello de mejora (glow) detrás de la torre ---
        if self.upgrade_anim_timer > 0:
            p = self.upgrade_anim_timer / self.upgrade_anim_duration  # 1 -> 0
            radius = int(40 + (1 - p) * 30)
            alpha = int(180 * p)
            glow = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(glow, (255, 220, 120, alpha), (radius, radius), radius)
            glow_pos = (self.x - radius, self.y - radius - 10)
            screen.blit(glow, glow_pos)

        # muzzle flash (bright ellipse) — position depends on facing/target
        if self.muzzle_timer > 0:
            p = self.muzzle_timer / self.muzzle_duration  # 1 -> 0
            flash_w = int(18 + (1 - p) * 36)
            flash_h = int(8 + (1 - p) * 16)
            # direction:
            if self.target:
                angle = math.atan2(self.target.y - self.y, self.target.x - self.x)
            else:
                angle = math.pi if self.facing_left else 0
            tip_x = self.x + math.cos(angle) * 36
            tip_y = self.y + math.sin(angle) * 36 - 6
            surf = pygame.Surface((flash_w, flash_h), pygame.SRCALPHA)
            pygame.draw.ellipse(surf, (255, 230, 140, int(220 * p)), (0, 0, flash_w, flash_h))
            screen.blit(surf, (tip_x - flash_w // 2, tip_y - flash_h // 2))

        # Dibujo de la torre
        screen.blit(img, rect)

        # Draw muzzle particles (behind top layer)
        for p in self.muzzle_particles:
            s = pygame.Surface((p["size"], p["size"]), pygame.SRCALPHA)
            color = p["color"]
            a = int(p.get("alpha", 255))
            pygame.draw.circle(s, (color[0], color[1], color[2], a), (p["size"] // 2, p["size"] // 2), p["size"] // 2)
            screen.blit(s, (p["x"] - p["size"] // 2, p["y"] - p["size"] // 2))

        # Badge que indica el nivel (siempre visible)
        badge_w, badge_h = 44, 20
        badge_x = self.x - badge_w // 2
        badge_y = self.y - rect.height // 2 - badge_h - 6
        badge_rect = pygame.Rect(badge_x, badge_y, badge_w, badge_h)
        pygame.draw.rect(screen, (120, 90, 50), badge_rect, border_radius=6)
        inner_badge = badge_rect.inflate(-4, -4)
        pygame.draw.rect(screen, (200, 170, 110), inner_badge, border_radius=5)

        lvl_label = self.level_font.render(f"Nivel {self.level}", True, (60, 40, 20))
        screen.blit(lvl_label, (inner_badge.centerx - lvl_label.get_width() // 2, inner_badge.centery - lvl_label.get_height() // 2))

        # Texto flotante al subir de nivel (sube y se desvanece)
        if self.level_label_timer > 0:
            anim_progress = 1 - (self.level_label_timer / self.level_label_duration)  # 0 -> 1
            float_y = int(-10 - anim_progress * 30)
            alpha = int(255 * (1 - anim_progress))
            t_surf = self.level_font.render(f"Nivel {self.level}", True, (255, 255, 255)).convert_alpha()
            # aplicar alpha
            t_surf.set_alpha(alpha)
            tx = self.x - t_surf.get_width() // 2
            ty = badge_y - 10 + float_y
            screen.blit(t_surf, (tx, ty))


# =========================
# TORRE DE ARQUEROS
# =========================
class MusketeerTower(BaseTower):
    def __init__(self, x, y):
        super().__init__(x, y)

        self.range = 150
        self.damage = 25
        self.fire_rate = 60

        self.cost = 50
        self.total_cost = self.cost

        self.load_image()

    def load_image(self):
        if self.level == 1:
            img_path = "assets/imagenes/towers/mosquetera1.png"
        elif self.level == 2:
            img_path = "assets/imagenes/towers/mosquetera2.png"
        else:
            img_path = "assets/imagenes/towers/mosquetera3.png"
        self.image = pygame.image.load(img_path).convert_alpha()
        self.image = pygame.transform.scale(self.image, (75, 100))
        self.rect = self.image.get_rect(center=(self.x, self.y))

    def shoot(self, enemy, projectiles, enemies):
        # spawn projectile
        projectiles.append(
            Arrow((self.x + ( -12 if self.facing_left else 12), self.y - 10), enemy, self.damage)
        )


# =========================
# TORRE DE CAÑÓN
# =========================
class CannonTower(BaseTower):
    def __init__(self, x, y):
        super().__init__(x, y)

        self.range = 130
        self.damage = 55
        self.fire_rate = 90

        self.cost = 100
        self.total_cost = self.cost

        self.load_image()

    def load_image(self):
        if self.level == 1:
            img_path = "assets/imagenes/towers/cañon1.png"
        elif self.level == 2:
            img_path = "assets/imagenes/towers/cañon2.png"
        else:
            img_path = "assets/imagenes/towers/cañon3.png"
        self.image = pygame.image.load(img_path).convert_alpha()
        self.image = pygame.transform.scale(self.image, (80, 60))
        self.rect = self.image.get_rect(center=(self.x, self.y))

    def shoot(self, enemy, projectiles, enemies):
        # AoE radius scales with level
        aoe = 60 + (self.level - 1) * 12
        projectiles.append(
            CannonBall((self.x, self.y), enemy, self.damage, enemies=enemies, aoe_radius=aoe)
        )


# =========================
# TORRE MÁGICA
# =========================
class MagicTower(BaseTower):
    def __init__(self, x, y):
        super().__init__(x, y)

        self.range = 160
        self.damage = 30
        self.fire_rate = 75

        self.cost = 150
        self.total_cost = self.cost

        self.load_image()

    def load_image(self):
        if self.level == 1:
            img_path = "assets/imagenes/towers/magica1.png"
        elif self.level == 2:
            img_path = "assets/imagenes/towers/magica2.png"
        else:
            img_path = "assets/imagenes/towers/magica3.png"
        self.image = pygame.image.load(img_path).convert_alpha()
        self.image = pygame.transform.scale(self.image, (75, 100))
        self.rect = self.image.get_rect(center=(self.x, self.y))

    def shoot(self, enemy, projectiles, enemies):
        # MagicMissile applies slow on impact (see entities/projectile.py)
        projectiles.append(
            MagicMissile((self.x, self.y - 10), enemy, self.damage)
        )