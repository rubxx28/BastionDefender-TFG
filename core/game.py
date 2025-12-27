import pygame
from settings import WIDTH, HEIGHT, FPS
from core.map import GameMap
from entities.enemy import Enemy
from entities.tower import MusketeerTower, CannonTower
from ui.tower_menu import BuildMenu

MENU = "menu"
GAME = "game"
GAME_OVER = "game_over"


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Bastion Defender")
        self.clock = pygame.time.Clock()

        self.font_title = pygame.font.SysFont("arialblack", 72)
        self.font_button = pygame.font.SysFont("arial", 36)
        self.font_hud = pygame.font.SysFont("arial", 22)
        self.font_wave = pygame.font.SysFont("arialblack", 40)
        self.font_big = pygame.font.SysFont("arialblack", 64)

        self.button_rect = pygame.Rect(WIDTH // 2 - 160, HEIGHT // 2 + 40, 320, 70)

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

        # Reset escalado enemigos
        Enemy.base_hp = 60
        Enemy.base_speed = min(1.6, Enemy.base_speed + 0.03)

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
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.button_rect.collidepoint(event.pos):
                        self.reset_game()
                        self.state = GAME

            elif self.state == GAME_OVER:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.button_rect.collidepoint(event.pos):
                        self.reset_game()
                        self.state = GAME

            elif self.state == GAME and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:

                # Menú abierto
                if self.build_menu:
                    choice = self.build_menu.handle_click(event.pos)

                    if choice == "archer" and self.gold >= 50:
                        self.towers.append(
                            MusketeerTower(self.selected_spot[0], self.selected_spot[1])
                        )
                        self.gold -= 50
                        self.game_map.tower_spots.remove(self.selected_spot)

                    elif choice == "cannon" and self.gold >= 100:
                        self.towers.append(
                            CannonTower(self.selected_spot[0], self.selected_spot[1])
                        )
                        self.gold -= 100
                        self.game_map.tower_spots.remove(self.selected_spot)

                    elif choice == "upgrade" and self.selected_tower:
                        if self.gold >= 75:
                            upgraded = self.selected_tower.upgrade()
                            if upgraded:
                                self.gold -= 75

                    self.build_menu = None
                    self.selected_spot = None
                    self.selected_tower = None
                    return

                # Click en torre → menú mejora
                for tower in self.towers:
                    if tower.rect.collidepoint(event.pos):
                        self.selected_tower = tower
                        self.build_menu = BuildMenu(tower.x, tower.y, has_tower=True)
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
        if self.state != GAME:
            return

        if self.lives <= 0:
            self.state = GAME_OVER
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
    # DRAW
    # -------------------------
    def draw_menu(self):
        self.screen.fill((25, 25, 25))
        title = self.font_title.render("BASTION DEFENDER", True, (200, 180, 120))
        self.screen.blit(title, title.get_rect(center=(WIDTH // 2, HEIGHT // 3)))

        pygame.draw.rect(self.screen, (120, 90, 50), self.button_rect)
        text = self.font_button.render("JUGAR", True, (255, 255, 255))
        self.screen.blit(text, text.get_rect(center=self.button_rect.center))

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

        self.screen.blit(self.font_hud.render(f"Vidas: {self.lives}", True, (255, 255, 255)), (10, 10))
        self.screen.blit(self.font_hud.render(f"Oro: {self.gold}", True, (255, 215, 0)), (10, 35))
        self.screen.blit(self.font_hud.render(f"Oleada: {self.wave}", True, (200, 200, 200)), (10, 60))

        if self.wave_message:
            text = self.font_wave.render(self.wave_message, True, (255, 200, 100))
            self.screen.blit(text, text.get_rect(center=(WIDTH // 2, HEIGHT // 6)))

        if self.show_countdown:
            text = self.font_wave.render(
                f"Oleada {self.wave} en {self.countdown}", True, (255, 215, 0)
            )
            self.screen.blit(text, text.get_rect(center=(WIDTH // 2, HEIGHT // 4)))

    def draw_game_over(self):
        self.screen.fill((15, 15, 15))
        title = self.font_big.render("GAME OVER", True, (200, 30, 30))
        self.screen.blit(title, title.get_rect(center=(WIDTH // 2, HEIGHT // 3)))

        score = self.font_wave.render(
            f"Oleadas superadas: {self.wave}", True, (255, 255, 255)
        )
        self.screen.blit(score, score.get_rect(center=(WIDTH // 2, HEIGHT // 2)))

        pygame.draw.rect(self.screen, (120, 90, 50), self.button_rect)
        text = self.font_button.render("JUGAR DE NUEVO", True, (255, 255, 255))
        self.screen.blit(text, text.get_rect(center=self.button_rect.center))

    def draw(self):
        if self.state == MENU:
            self.draw_menu()
        elif self.state == GAME:
            self.draw_game()
        elif self.state == GAME_OVER:
            self.draw_game_over()

        pygame.display.flip()
