import pygame
import os
import requests
import time
import math
import random
from settings import WIDTH, HEIGHT, FPS
from core.map import GameMap
from entities.enemy import Enemy
from entities.miniboss import MiniBoss
from entities.tower import MusketeerTower, CannonTower, MagicTower
from ui.tower_menu import BuildMenu
from ui.menu_screen import MenuScreen
from ui.gameover_screen import GameOverScreen
from ui.hud import HUD
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

        # Interfaces UI
        self.menu_screen = MenuScreen()
        self.gameover_screen = GameOverScreen()
        self.hud = HUD()

        # Sonido
        try:
            self.snd_click = pygame.mixer.Sound(
                "assets/sonidos/menu_click.wav")
        except Exception:
            self.snd_click = None

        self.running = True
        self.state = MENU

        self.reset_game()

    # -------------------------
    # RESET
    # -------------------------
    def reset_game(self):
        self.game_map = GameMap()
        self.enemies = []
        self.towers = []
        self.projectiles = []
        self.miniboss = None
        
        self.start_time = time.time()

        # Velocidad del juego (0 = parado, 1 = normal, 2 = doble velocidad)
        self.game_speed = 1

        self.spawn_timer = 0
        self.spawn_delay = 80

        self.lives = 10
        self.gold = 350

        # Oleadas
        self.wave = 1
        self.enemies_to_spawn = 10
        self.enemies_spawned = 0
        self.between_waves = False
        self.wave_timer = 0
        self.miniboss_spawned_this_wave = False  # Para controlar que solo salga 1 vez

        # Mensaje oleada
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

        self.start_time = time.time()
        self.score_sent = False
        # Generar/recuperar player_id persistente para esta instalación (sin login)
        # Prioridad: 1) PLAYER_ID env var 2) archivo player_id.txt en la raíz del proyecto 3) generar nuevo y guardarlo
        try:
            from pathlib import Path
            root = Path(__file__).resolve().parents[1]
            pid_file = root / "player_id.txt"
        except Exception:
            pid_file = None

        pid_env = os.getenv('PLAYER_ID')
        if pid_env:
            try:
                self.player_id = int(pid_env)
                # si hay pid_file, actualizarlo para consistencia
                if pid_file:
                    try:
                        pid_file.write_text(str(self.player_id))
                    except Exception:
                        pass
            except Exception:
                # env var inválida -> continuar con fichero/generación
                self.player_id = None
        else:
            self.player_id = None

        # Si no viene por env, intentar leer fichero
        if self.player_id is None and pid_file and pid_file.exists():
            try:
                val = pid_file.read_text().strip()
                self.player_id = int(val)
            except Exception:
                self.player_id = None

        # Si aún no hay player_id, generar uno nuevo y guardarlo
        if self.player_id is None:
            self.player_id = random.randint(100000, 999999)
            if pid_file:
                try:
                    pid_file.write_text(str(self.player_id))
                except Exception:
                    pass

    def set_player_id(self, player_id):
        """Asignar player_id desde código (ej: flujo de login o app móvil)."""
        try:
            self.player_id = int(player_id)
        except Exception:
            self.player_id = None


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
                if event.type == pygame.MOUSEMOTION:
                    self.menu_screen.handle_hover(event.pos)
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.menu_screen.handle_click(event.pos):
                        if self.snd_click:
                            self.snd_click.play()
                        self.reset_game()
                        self.state = GAME

            elif self.state == GAME_OVER:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    result = self.gameover_screen.handle_click(event.pos)
                    if result == "retry":
                        if self.snd_click:
                            self.snd_click.play()
                        self.reset_game()
                        self.state = GAME
                    elif result == "exit":
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
                            # Guardar el costo ANTES de mejorar (upgrade() lo recalcula)
                            cost = self.selected_tower.upgrade_cost
                            upgraded = self.selected_tower.upgrade()
                            if upgraded:
                                self.gold -= cost

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
                        # Generar opciones dinámicas basadas en lógica del juego
                        options = []
                        if tower.level >= tower.max_level:
                            options.append(("max", "Nivel máximo"))
                        else:
                            options.append(("upgrade", f"Mejorar - {tower.upgrade_cost} oro"))
                        refund = int(tower.total_cost / 2)
                        options.append(("sell", f"Derribar - {refund} oro"))
                        
                        self.build_menu = BuildMenu(tower.x, tower.y, options)
                        return

                # Click en botones de velocidad
                speed_button = self.hud.get_speed_button_clicked(event.pos)
                if speed_button is not None:
                    self.set_game_speed(speed_button)
                    self.hud.set_current_speed(self.game_speed)
                    if self.snd_click:
                        try:
                            self.snd_click.play()
                        except Exception:
                            pass
                    return

                # Click en círculo → menú construcción
                for spot in self.game_map.tower_spots:
                    if pygame.math.Vector2(spot).distance_to(event.pos) < 25:
                        self.selected_spot = spot
                        # Opciones de construcción con costos
                        options = [
                            ("archer", "Mosqueteros - 50 oro"),
                            ("cannon", "Cañón - 100 oro"),
                            ("magic", "Mago - 150 oro")
                        ]
                        self.build_menu = BuildMenu(spot[0], spot[1], options)
                        return

    # -------------------------
    # UPDATE
    # -------------------------
    def update(self):
        # Si estamos en portada, actualizar animaciones
        if self.state == MENU:
            self.menu_screen.update()
            return

        if self.state != GAME:
            # Si estamos en game over, actualizar pantalla
            if self.state == GAME_OVER:
                self.gameover_screen.update()
            return

        if self.lives <= 0:
            self.send_score()
            self.state = GAME_OVER
            return

        if self.wave_message_timer > 0:
            self.wave_message_timer -= 1
        else:
            self.wave_message = ""

        if self.show_countdown:
            self.countdown_timer -= 1 * self.game_speed
            if self.countdown_timer <= 0:
                self.countdown -= 1
                self.countdown_timer = FPS
                if self.countdown == 0:
                    self.show_countdown = False
            return

        if self.between_waves:
            self.wave_timer += 1 * self.game_speed
            if self.wave_timer >= FPS * 3:
                self.between_waves = False
                self.wave += 1
                self.enemies_spawned = 0
                self.enemies_to_spawn += 2
                self.spawn_delay = max(40, self.spawn_delay - 3)
                self.miniboss_spawned_this_wave = False  # Reset miniboss flag

                # 🔥 MINIBOSS cada 5 oleadas
                if self.wave % 5 == 0:
                    self.miniboss = MiniBoss(self.game_map.get_path(), boss_index=0)
                    self.wave_message = f"¡¡¡ MINIJEFE EN OLEADA {self.wave} !!!"
                else:
                    self.wave_message = f"OLEADA {self.wave}"

                self.wave_message_timer = FPS * 2

                Enemy.base_hp += 15
                Enemy.base_speed = min(2.2, Enemy.base_speed + 0.03)

                self.show_countdown = True
                self.countdown = 3
                self.countdown_timer = FPS
                self.wave_timer = 0
            return

        if self.game_speed > 0:  # Solo actualizar si el juego no está pausado
            if self.enemies_spawned < self.enemies_to_spawn:
                self.spawn_timer += 1 * self.game_speed
                if self.spawn_timer >= self.spawn_delay:
                    self.enemies.append(Enemy(self.game_map.get_path()))
                    self.enemies_spawned += 1
                    self.spawn_timer = 0

            for enemy in self.enemies[:]:
                for _ in range(self.game_speed):
                    if not enemy.alive:
                        break
                    enemy.update()
                if not enemy.alive:
                    self.enemies.remove(enemy)
                    if enemy.reached_goal:
                        self.lives -= 1
                    else:
                        self.gold += 10

            # Actualizar miniboss si existe
            if self.miniboss:
                for _ in range(self.game_speed):
                    if not self.miniboss.alive:
                        break
                    self.miniboss.update()
                if not self.miniboss.alive:
                    if self.miniboss.reached_goal:
                        self.lives -= 1
                    else:
                        self.gold += 50  # MiniBoss da más oro
                    self.miniboss = None

            for tower in self.towers:
                # Pasar miniboss además de enemigos para que las torres lo ataquen
                targets = self.enemies.copy()
                if self.miniboss:
                    targets.append(self.miniboss)
                for _ in range(self.game_speed):
                    tower.update(targets, self.projectiles)

            for proj in self.projectiles[:]:
                for _ in range(self.game_speed):
                    if not proj.alive:
                        break
                    proj.update()
                if not proj.alive:
                    self.projectiles.remove(proj)

        if self.enemies_spawned == self.enemies_to_spawn and not self.enemies and not self.miniboss:
            self.between_waves = True

    # -------------------------
    # GAME SPEED CONTROL
    # -------------------------
    def set_game_speed(self, speed):
        """Cambiar la velocidad del juego (0=pauso, 1=normal, 2=doble)"""
        if speed in (0, 1, 2):
            self.game_speed = speed
            if speed == 0:
                self.wave_message = "PAUSADO"
            elif speed == 1:
                self.wave_message = "VELOCIDAD NORMAL"
            else:
                self.wave_message = "VELOCIDAD 2x"
            self.wave_message_timer = FPS * 2

    # -------------------------
    # MENU helpers (visual only)
    # -------------------------
    def draw_tooltip(self, lines, pos):
        padding = 6
        font = pygame.font.SysFont("arial", 14)
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
        self.menu_screen.draw(self.screen)

    def draw_game(self):
        self.game_map.draw(self.screen)

        occupied = [t.rect.center for t in self.towers]
        self.game_map.draw_tower_spots(self.screen, occupied)

        for tower in self.towers:
            tower.draw(self.screen)

        for enemy in self.enemies:
            enemy.draw(self.screen)

        # Dibujar miniboss si existe
        if self.miniboss:
            self.miniboss.draw(self.screen)

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
                pass

            # Tooltip junto al cursor
            self.draw_tooltip(lines, (mouse[0] + 12, mouse[1] + 12))

        # Preview de alcance al abrir menú de construcción sobre un spot
        if self.build_menu and self.selected_spot:
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
        # HUD
        # -------------------
        self.hud.set_current_speed(self.game_speed)
        self.hud.draw(self.screen, self.lives, self.gold, self.wave, self.player_id)
        
        # Mensaje de oleada
        if self.wave_message_timer > 0:
            self.hud.draw_wave_message(self.screen, self.wave_message, 
                                      self.wave_message_timer, FPS * 2)
        
        # Cuenta atrás
        if self.show_countdown:
            self.hud.draw_countdown(self.screen, self.countdown)
        
        # Overlay PAUSADO cuando la velocidad es 0
        if self.game_speed == 0 and self.state == GAME:
            try:
                font = pygame.font.SysFont("arialblack", 60)
            except Exception:
                font = pygame.font.SysFont("arial", 48)
            text = font.render("PAUSADO", True, (255, 255, 255))
            # Fondo semitransparente
            s = pygame.Surface((text.get_width() + 40, text.get_height() + 24), pygame.SRCALPHA)
            s.fill((0, 0, 0, 160))
            x = WIDTH//2 - s.get_width()//2
            y = HEIGHT//2 - s.get_height()//2
            self.screen.blit(s, (x, y))
            self.screen.blit(text, (x + 20, y + 12))

    def draw_game_over(self):
        self.gameover_screen.draw(self.screen, self.wave, self.gold, self.player_id)

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
        
    def send_score(self):
        # Evitar reenvíos
        if getattr(self, "score_sent", False):
            return

        # Validar player_id
        if not hasattr(self, 'player_id') or self.player_id is None:
            # No hay identificador de jugador; no enviamos
            return

        payload = {
            "player_id": self.player_id,
            "waves": self.wave,
            "duration_seconds": int(time.time() - self.start_time),
        }

        try:
            resp = requests.post("http://127.0.0.1:8000/score", json=payload, timeout=3)
            if 200 <= resp.status_code < 300:
                self.score_sent = True
        except Exception:
            # Error de red/timeout - silently fail
            pass

    