import pygame
import requests
import time
import math
import random
from settings import WIDTH, HEIGHT, FPS
from core.map import GameMap
from entities.enemy import Enemy
from entities.tower import MusketeerTower, CannonTower, MagicTower
from ui.tower_menu import BuildMenu
from datetime import datetime

MENU = "menu"
GAME = "game"
GAME_OVER = "game_over"


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Bastion Defender")
        self.clock = pygame.time.Clock()

        # Fuentes
        self.font_title = pygame.font.SysFont("arialblack", 72)
        self.font_button = pygame.font.SysFont("arial", 36)
        self.font_hud = pygame.font.SysFont("arial", 22)
        self.font_wave = pygame.font.SysFont("arialblack", 40)
        self.font_big = pygame.font.SysFont("arialblack", 64)
        self.font_small = pygame.font.SysFont("arial", 14)
        self.font_countdown = pygame.font.SysFont("arialblack", 96)

        # Botones portada / game over
        self.button_rect = pygame.Rect(
            WIDTH // 2 - 160, HEIGHT // 2 + 40, 320, 70)
        self.retry_button_rect = pygame.Rect(
            WIDTH // 2 - 140, HEIGHT // 2 + 30, 120, 50)
        self.exit_button_rect = pygame.Rect(
            WIDTH // 2 + 20, HEIGHT // 2 + 30, 120, 50)

        self.running = True
        self.state = MENU

        # Visuals de portada
        try:
            self.menu_bg = pygame.image.load(
                "assets/imagenes/ui/menu_bg.png").convert()
            self.menu_bg = pygame.transform.smoothscale(
                self.menu_bg, (WIDTH, HEIGHT))
        except Exception:
            self.menu_bg = None
        try:
            self.logo = pygame.image.load(
                "assets/imagenes/ui/logo.png").convert_alpha()
        except Exception:
            self.logo = None

        self.menu_pulse = 0.0
        self.menu_particles = []
        self.menu_particle_timer = 0

        # Visuals Game Over
        self.game_over_alpha = 0
        self.game_over_shown = False
        self.gameover_particles = []

        # Opcional sonido click
        try:
            self.snd_click = pygame.mixer.Sound(
                "assets/sonidos/menu_click.wav")
        except Exception:
            self.snd_click = None

        self.reset_game()

    # -------------------------
    # RESET
    # -------------------------
    def reset_game(self):
        self.game_map = GameMap()
        self.enemies = []
        self.towers = []
        self.projectiles = []

        self.spawn_timer = 0
        self.spawn_delay = 80

        self.lives = 10
        self.gold = 100

        # Oleadas
        self.wave = 1
        self.enemies_to_spawn = 4
        self.enemies_spawned = 0
        self.between_waves = False
        self.wave_timer = 0

        # Mensaje oleada (no se muestra en banner ahora)
        self.wave_message = ""
        self.wave_message_timer = 0

        # Cuenta atrás
        self.countdown = 3
        self.countdown_timer = FPS
        self.show_countdown = False

        # Menú
        self.build_menu = None
        self.selected_spot = None
        self.selected_tower = None

        # Reset escalado enemigos (restaurar base)
        Enemy.base_hp = 60
        Enemy.base_speed = 0.55

        # Reset visual Game Over
        self.game_over_alpha = 0
        self.game_over_shown = False
        self.gameover_particles = []
        self.start_time = time.time()
        self.score_sent = False


    # -------------------------
    # LOOP
    # -------------------------
    def run(self):
        while self.running:
            self.clock.tick(FPS)
            self.handle_events()
            self.update()
            self.draw()
        pygame.quit()

    # -------------------------
    # EVENTOS
    # -------------------------
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if self.state == MENU:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.button_rect.collidepoint(event.pos):
                        if self.snd_click:
                            self.snd_click.play()
                        self.reset_game()
                        self.state = GAME

            elif self.state == GAME_OVER:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.retry_button_rect.collidepoint(event.pos):
                        if self.snd_click:
                            self.snd_click.play()
                        self.reset_game()
                        self.state = GAME
                    elif self.exit_button_rect.collidepoint(event.pos):
                        if self.snd_click:
                            self.snd_click.play()
                        self.running = False

            elif self.state == GAME and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:

                # Menú abierto
                if self.build_menu:
                    choice = self.build_menu.handle_click(event.pos)

                    if choice == "archer" and self.gold >= 50:
                        self.towers.append(MusketeerTower(
                            self.selected_spot[0], self.selected_spot[1]))
                        self.gold -= 50
                        self.game_map.tower_spots.remove(self.selected_spot)

                    elif choice == "cannon" and self.gold >= 100:
                        self.towers.append(CannonTower(
                            self.selected_spot[0], self.selected_spot[1]))
                        self.gold -= 100
                        self.game_map.tower_spots.remove(self.selected_spot)
                    elif choice == "magic" and self.gold >= 150:
                        self.towers.append(MagicTower(
                            self.selected_spot[0], self.selected_spot[1]))
                        self.gold -= 150
                        self.game_map.tower_spots.remove(self.selected_spot)

                    elif choice == "upgrade" and self.selected_tower:
                        if self.gold >= self.selected_tower.upgrade_cost:
                            upgraded = self.selected_tower.upgrade()
                            if upgraded:
                                self.gold -= self.selected_tower.upgrade_cost

                    elif choice == "sell" and self.selected_tower:
                        refund = int(self.selected_tower.total_cost / 2)
                        self.gold += refund
                        # devolver el spot
                        self.game_map.tower_spots.append(
                            (self.selected_tower.x, self.selected_tower.y))
                        # quitar la torre
                        if self.selected_tower in self.towers:
                            self.towers.remove(self.selected_tower)

                    self.build_menu = None
                    self.selected_spot = None
                    self.selected_tower = None
                    return

                # Click en torre → menú mejora
                for tower in self.towers:
                    if tower.rect.collidepoint(event.pos):
                        self.selected_tower = tower
                        self.build_menu = BuildMenu(
                            tower.x, tower.y, has_tower=True, tower=tower)
                        return

                # Click en círculo → menú construcción
                for spot in self.game_map.tower_spots:
                    if pygame.math.Vector2(spot).distance_to(event.pos) < 25:
                        self.selected_spot = spot
                        self.build_menu = BuildMenu(spot[0], spot[1])
                        return

    # -------------------------
    # UPDATE
    # -------------------------
    def update(self):
        # Si estamos en portada, actualizar animaciones de portada
        if self.state == MENU:
            self.update_menu()
            return

        if self.state != GAME:
            # si estamos en game over, avanzar fade/anim (sin entrar al loop de juego)
            if self.state == GAME_OVER:
                # fade-in overlay and spawn particles once
                if not self.game_over_shown:
                    self.game_over_alpha = 0
                    self.gameover_particles = []
                    for _ in range(18):
                        self.gameover_particles.append({
                            "x": random.randint(0, WIDTH),
                            "y": random.randint(-40, -10),
                            "vx": random.uniform(-0.4, 0.4),
                            "vy": random.uniform(1.0, 2.4),
                            "life": random.randint(40, 80),
                            "size": random.randint(3, 6),
                            "alpha": 255
                        })
                    self.game_over_shown = True
                self.game_over_alpha = min(200, self.game_over_alpha + 10)
            return

        if self.lives <= 0:

            if not self.score_sent:
                duration = int(time.time() - self.start_time)

                payload = {
                    "waves": self.wave,
                    "duration_seconds": duration,
                    "played_at": datetime.now().isoformat()
                }

                try:
                    requests.post(
                        "http://127.0.0.1:8000/score",
                        json=payload,
                        timeout=2
                )
                    print("Puntuación enviada: ", payload)
                except Exception as e:
                    print("Error al enviar puntuación: ", e)
                    

                self.score_sent = True

            self.state = GAME_OVER
            self.game_over_shown = False
            return


        if self.wave_message_timer > 0:
            self.wave_message_timer -= 1
        else:
            self.wave_message = ""

        if self.show_countdown:
            self.countdown_timer -= 1
            if self.countdown_timer <= 0:
                self.countdown -= 1
                self.countdown_timer = FPS
                if self.countdown == 0:
                    self.show_countdown = False
            return

        if self.between_waves:
            self.wave_timer += 1
            if self.wave_timer >= FPS * 3:
                self.between_waves = False
                self.wave += 1
                self.enemies_spawned = 0
                self.enemies_to_spawn += 2
                self.spawn_delay = max(40, self.spawn_delay - 3)

                self.wave_message = f"OLEADA {self.wave}"
                self.wave_message_timer = FPS * 2

                Enemy.base_hp += 15
                Enemy.base_speed = min(2.2, Enemy.base_speed + 0.03)

                self.show_countdown = True
                self.countdown = 3
                self.countdown_timer = FPS
                self.wave_timer = 0
            return

        if self.enemies_spawned < self.enemies_to_spawn:
            self.spawn_timer += 1
            if self.spawn_timer >= self.spawn_delay:
                # spawnear enemigo (mismo comportamiento que antes)
                # si quieres variar tipos a futuro, aquí se puede cambiar
                self.enemies.append(Enemy(self.game_map.get_path()))
                self.enemies_spawned += 1
                self.spawn_timer = 0

        for enemy in self.enemies[:]:
            enemy.update()
            if not enemy.alive:
                self.enemies.remove(enemy)
                if enemy.reached_goal:
                    self.lives -= 1
                else:
                    self.gold += 10

        for tower in self.towers:
            tower.update(self.enemies, self.projectiles)

        for proj in self.projectiles[:]:
            proj.update()
            if not proj.alive:
                self.projectiles.remove(proj)

        if self.enemies_spawned == self.enemies_to_spawn and not self.enemies:
            self.between_waves = True

    # -------------------------
    # MENU helpers (visual only)
    # -------------------------
    def update_menu(self):
        self.menu_pulse += 0.04
        self.menu_particle_timer -= 1
        if self.menu_particle_timer <= 0:
            self.menu_particle_timer = random.randint(6, 18)
            cx = WIDTH // 2 + random.randint(-160, 160)
            cy = int(HEIGHT * 0.22) + random.randint(-14, 14)
            self.menu_particles.append({
                "x": cx,
                "y": cy,
                "vx": random.uniform(-0.2, 0.2),
                "vy": random.uniform(-0.6, 0.2),
                "life": random.randint(20, 42),
                "size": random.randint(2, 4),
                "alpha": 220
            })
        for p in self.menu_particles[:]:
            p["x"] += p["vx"]
            p["y"] += p["vy"]
            p["vy"] += 0.02
            p["life"] -= 1
            p["alpha"] = max(0, p["alpha"] - 6)
            if p["life"] <= 0:
                self.menu_particles.remove(p)

    def draw_tooltip(self, lines, pos):
        padding = 6
        font = self.font_small
        width = max(font.render(l, True, (0, 0, 0)).get_width()
                    for l in lines) + padding * 2
        height = sum(font.render(l, True, (0, 0, 0)).get_height()
                     for l in lines) + padding * 2 + (len(lines)-1) * 2
        surf = pygame.Surface((width, height), pygame.SRCALPHA)
        pygame.draw.rect(surf, (20, 20, 20, 230),
                         (0, 0, width, height), border_radius=6)
        pygame.draw.rect(surf, (200, 170, 110, 200),
                         (2, 2, width-4, height-4), 2, border_radius=6)
        y = padding
        for l in lines:
            text = font.render(l, True, (240, 240, 240))
            surf.blit(text, (padding, y))
            y += text.get_height() + 2
        x, y = pos
        if x + width > WIDTH:
            x = WIDTH - width - 8
        if y + height > HEIGHT:
            y = HEIGHT - height - 8
        self.screen.blit(surf, (x, y))

    # -------------------------
    # DRAW helpers
    # -------------------------
    def draw_menu(self):
        # Fondo: imagen si hay, si no degradado
        if self.menu_bg:
            self.screen.blit(self.menu_bg, (0, 0))
        else:
            for i in range(0, HEIGHT, 8):
                t = i / HEIGHT
                c = int(30 + 100 * t)
                # clamp to valid 0-255 range
                r = max(0, min(255, c))
                g = max(0, min(255, c - 6))
                b = max(0, min(255, c - 36))
                pygame.draw.rect(self.screen, (r, g, b), (0, i, WIDTH, 8))

        # Partículas detrás del logo
        for p in self.menu_particles:
            surf = pygame.Surface((p["size"], p["size"]), pygame.SRCALPHA)
            pygame.draw.circle(surf, (255, 230, 150, int(
                p["alpha"])), (p["size"] // 2, p["size"] // 2), p["size"] // 2)
            self.screen.blit(
                surf, (p["x"] - p["size"] // 2, p["y"] - p["size"] // 2))

        # Logo con pulso
        pulse = 1.0 + math.sin(self.menu_pulse) * 0.04
        logo_w, logo_h = 520, 120
        if self.logo:
            scaled = pygame.transform.smoothscale(
                self.logo, (int(logo_w * pulse), int(logo_h * pulse)))
            self.screen.blit(scaled, scaled.get_rect(
                center=(WIDTH // 2, int(HEIGHT * 0.23))))
        else:
            shadow = self.font_title.render(
                "BASTION DEFENDER", True, (20, 20, 20))
            title = self.font_title.render(
                "BASTION DEFENDER", True, (235, 200, 120))
            self.screen.blit(shadow, shadow.get_rect(
                center=(WIDTH // 2 + 3, int(HEIGHT * 0.23) + 3)))
            self.screen.blit(title, title.get_rect(
                center=(WIDTH // 2, int(HEIGHT * 0.23))))

        # Botón JUGAR (sombra, gradient, outline)
        mouse = pygame.mouse.get_pos()
        hover = self.button_rect.collidepoint(mouse)
        pygame.draw.rect(self.screen, (20, 20, 20),
                         self.button_rect.move(4, 6), border_radius=10)
        top = (235, 195, 80) if hover else (200, 160, 60)
        bot = (200, 145, 40) if hover else (170, 125, 32)
        pygame.draw.rect(self.screen, top, self.button_rect, border_radius=10)
        pygame.draw.rect(self.screen, bot,
                         self.button_rect.inflate(-4, -4), border_radius=8)
        pygame.draw.rect(self.screen, (90, 60, 30),
                         self.button_rect, 3, border_radius=10)
        label = self.font_button.render("JUGAR", True, (24, 20, 16))
        if hover:
            label = pygame.transform.smoothscale(
                label, (int(label.get_width() * 1.03), int(label.get_height() * 1.03)))
        self.screen.blit(label, label.get_rect(center=self.button_rect.center))

        # Hint y créditos
        hint = self.font_small.render(
            "Click para empezar · Pulsa Esc para salir", True, (220, 220, 220))
        self.screen.blit(hint, (WIDTH // 2 - hint.get_width() //
                         2, self.button_rect.bottom + 12))
        credit = self.font_small.render(
            "Hecho con ♥ - Bastion Team", True, (195, 175, 140))
        self.screen.blit(credit, (12, HEIGHT - 24))

    def draw_game(self):
        self.game_map.draw(self.screen)

        occupied = [t.rect.center for t in self.towers]
        self.game_map.draw_tower_spots(self.screen, occupied)

        for tower in self.towers:
            tower.draw(self.screen)

        for enemy in self.enemies:
            enemy.draw(self.screen)

        for proj in self.projectiles:
            proj.draw(self.screen)

        if self.build_menu:
            self.build_menu.draw(self.screen)

        # -------------------
        # Tooltip y preview de alcance
        # -------------------
        mouse = pygame.mouse.get_pos()

        # Tooltip y rango al pasar por encima de una torre
        hovered_tower = None
        for tower in self.towers:
            if tower.rect.collidepoint(mouse):
                hovered_tower = tower
                break

        if hovered_tower:
            # Calcula DPS aproximado (damage * shots por segundo)
            dps = hovered_tower.damage * \
                (FPS / max(1, hovered_tower.fire_rate))
            upgrade_text = f"Mejorar: {hovered_tower.upgrade_cost} oro" if hovered_tower.level < hovered_tower.max_level else "Nivel máximo"
            lines = [f"Nivel {hovered_tower.level}", f"DPS: {dps:.1f}",
                     f"Alcance: {hovered_tower.range}", upgrade_text]

            # Rango (círculo semitransparente)
            r = hovered_tower.range
            try:
                s = pygame.Surface((r*2, r*2), pygame.SRCALPHA)
                pygame.draw.circle(s, (40, 200, 40, 60), (r, r), r)
                self.screen.blit(s, (hovered_tower.x - r, hovered_tower.y - r))
            except Exception:
                pass  # proteccion si r es muy grande/invalido

            # Tooltip junto al cursor
            self.draw_tooltip(lines, (mouse[0] + 12, mouse[1] + 12))

        # Preview de alcance al abrir menú de construcción sobre un spot
        if self.build_menu and not self.build_menu.has_tower and self.selected_spot:
            hovered = self.build_menu.get_hover(mouse)
            if hovered in ("archer", "cannon", "magic"):
                range_map = {"archer": 150, "cannon": 130, "magic": 160}
                cost_map = {"archer": 50, "cannon": 100, "magic": 150}
                r = range_map.get(hovered, 140)
                s = pygame.Surface((r*2, r*2), pygame.SRCALPHA)
                pygame.draw.circle(s, (60, 160, 220, 60), (r, r), r)
                self.screen.blit(s, (self.selected_spot[0] - r, self.selected_spot[1] - r))

                lines = [f"{hovered.capitalize()}", f"Coste: {cost_map[hovered]} oro", f"Alcance: {r}"]
                self.draw_tooltip(lines, (mouse[0] + 12, mouse[1] + 12))

        # -------------------
        # HUD (normal)
        # -------------------
        self.screen.blit(self.font_hud.render(
            f"Vidas: {self.lives}", True, (255, 255, 255)), (10, 10))
        self.screen.blit(self.font_hud.render(
            f"Oro: {self.gold}", True, (255, 215, 0)), (10, 35))
        self.screen.blit(self.font_hud.render(
            f"Oleada: {self.wave}", True, (200, 200, 200)), (10, 60))

        # -------------------
        # Cuenta atrás: "Oleada N" + número grande (3,2,1)
        # -------------------
        if self.show_countdown:
            subtitle_text = f"Oleada {self.wave}"
            subtitle = self.font_wave.render(subtitle_text, True, (255, 215, 0))
            number = self.font_countdown.render(str(self.countdown), True, (255, 235, 140))

            spacing = 22
            total_w = subtitle.get_width() + spacing + number.get_width()
            x0 = WIDTH // 2 - total_w // 2
            y_center = int(HEIGHT * 0.32)

            # Sombra para subtítulo
            shadow = self.font_wave.render(subtitle_text, True, (24, 18, 8))
            self.screen.blit(shadow, (x0 + 3, y_center - subtitle.get_height() // 2 + 3))
            # Subtítulo principal
            self.screen.blit(subtitle, (x0, y_center - subtitle.get_height() // 2))

            # Contorno ligero para número (simula glow/outline)
            n_x = x0 + subtitle.get_width() + spacing
            n_y = y_center - number.get_height() // 2
            for dx, dy in [(-4, 0), (4, 0), (0, -4), (0, 4), (-2, -2), (2, 2)]:
                n_shadow = self.font_countdown.render(str(self.countdown), True, (30, 20, 10))
                self.screen.blit(n_shadow, (n_x + dx, n_y + dy))
            # Número principal
            self.screen.blit(number, (n_x, n_y))

    def draw_game_over(self):
        # overlay oscuro con alpha
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((8, 8, 10, self.game_over_alpha))
        self.screen.blit(overlay, (0, 0))

        # partículas tipo confetti / brillo
        for p in self.gameover_particles[:]:
            p["x"] += p["vx"]
            p["y"] += p["vy"]
            p["vy"] += 0.04
            p["life"] -= 1
            p["alpha"] = max(0, p.get("alpha", 255) - 3)
            if p["life"] > 0:
                surf = pygame.Surface((p["size"], p["size"]), pygame.SRCALPHA)
                pygame.draw.circle(surf, (255, 200, 120, int(
                    p["alpha"])), (p["size"] // 2, p["size"] // 2), p["size"] // 2)
                self.screen.blit(surf, (p["x"], p["y"]))
            else:
                self.gameover_particles.remove(p)

        # Titular "GAME OVER" con glow
        for off in range(8, 0, -2):
            s = self.font_big.render("GAME OVER", True, (40, 12, 12))
            self.screen.blit(s, s.get_rect(
                center=(WIDTH // 2 + off, HEIGHT // 3 + off)))
        title = self.font_big.render("GAME OVER", True, (240, 90, 90))
        self.screen.blit(title, title.get_rect(
            center=(WIDTH // 2, HEIGHT // 3)))

        # Subtitulo con oleadas
        subtitle = self.font_wave.render(
            f"Oleadas superadas: {self.wave}", True, (240, 210, 150))
        self.screen.blit(subtitle, subtitle.get_rect(
            center=(WIDTH // 2, HEIGHT // 3 + 80)))

        # Botones Reintentar / Salir
        mouse = pygame.mouse.get_pos()
        rhover = self.retry_button_rect.collidepoint(mouse)
        ehover = self.exit_button_rect.collidepoint(mouse)

        pygame.draw.rect(self.screen, (230, 190, 80) if rhover else (
            200, 160, 60), self.retry_button_rect, border_radius=8)
        pygame.draw.rect(self.screen, (90, 60, 30),
                         self.retry_button_rect, 3, border_radius=8)
        rl = self.font_button.render("Reintentar", True, (24, 20, 16))
        self.screen.blit(rl, rl.get_rect(center=self.retry_button_rect.center))

        pygame.draw.rect(self.screen, (230, 190, 80) if ehover else (
            200, 160, 60), self.exit_button_rect, border_radius=8)
        pygame.draw.rect(self.screen, (90, 60, 30),
                         self.exit_button_rect, 3, border_radius=8)
        el = self.font_button.render("Salir", True, (24, 20, 16))
        self.screen.blit(el, el.get_rect(center=self.exit_button_rect.center))

    # -------------------------
    # CENTRAL DRAW (delegates)
    # -------------------------
    def draw(self):
        if self.state == MENU:
            self.draw_menu()
        elif self.state == GAME:
            self.draw_game()
        elif self.state == GAME_OVER:
            self.draw_game()
            self.draw_game_over()

        pygame.display.flip()