import pygame
from settings import WIDTH, HEIGHT, FPS
from core.map import GameMap
from entities.enemy import Enemy
from entities.tower import Tower

MENU = "menu"
GAME = "game"
GAME_OVER = "game_over"


class Game:
    def __init__(self):
        pygame.init()

        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Bastion Defender")
        self.clock = pygame.time.Clock()

        self.running = True
        self.state = MENU

        # Fuentes
        self.font_title = pygame.font.SysFont("arialblack", 72)
        self.font_button = pygame.font.SysFont("arial", 36)
        self.font_hud = pygame.font.SysFont("arial", 24)
        self.font_gameover = pygame.font.SysFont("arialblack", 64)

        # Botón menú
        self.button_rect = pygame.Rect(WIDTH // 2 - 160, HEIGHT // 2 + 40, 320, 70)

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
        self.spawn_delay = 120

        self.lives = 10
        self.gold = 100

    # -------------------------
    # BUCLE PRINCIPAL
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

            elif self.state == GAME:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    # CLICK IZQUIERDO → colocar torre
                    if event.button == 1:
                        for spot in self.game_map.tower_spots:
                            ocupado = any(t.rect.center == spot for t in self.towers)
                            if not ocupado:
                                if pygame.math.Vector2(spot).distance_to(event.pos) < 20:
                                    if self.gold >= 50:
                                        self.towers.append(Tower(spot))
                                        self.gold -= 50
                                    break

                    # CLICK DERECHO → mejorar torre
                    elif event.button == 3:
                        for tower in self.towers:
                            if tower.rect.collidepoint(event.pos):
                                if self.gold >= 75 and tower.level == 1:
                                    tower.upgrade()
                                    self.gold -= 75

            elif self.state == GAME_OVER:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.state = MENU

    # -------------------------
    # UPDATE
    # -------------------------
    def update(self):
        if self.state != GAME:
            return

        # Spawn enemigos
        self.spawn_timer += 1
        if self.spawn_timer >= self.spawn_delay:
            self.enemies.append(Enemy(self.game_map.get_path()))
            self.spawn_timer = 0

        # Actualizar enemigos
        for enemy in self.enemies[:]:
            enemy.update()

            if not enemy.alive:
                self.enemies.remove(enemy)

                if enemy.reached_goal:
                    self.lives -= 1      # ❌ pierde vida
                else:
                    self.gold += 10      # 💰 gana oro

        # Actualizar torres
        for tower in self.towers:
            tower.update(self.enemies, self.projectiles)

        # Actualizar proyectiles
        for projectile in self.projectiles[:]:
            projectile.update()
            if not projectile.alive:
                self.projectiles.remove(projectile)

        # GAME OVER
        if self.lives <= 0:
            self.state = GAME_OVER

    # -------------------------
    # DIBUJO MENU
    # -------------------------
    def draw_menu(self):
        self.screen.fill((25, 25, 25))

        title = self.font_title.render(
            "BASTION DEFENDER", True, (200, 180, 120)
        )
        self.screen.blit(
            title, title.get_rect(center=(WIDTH // 2, HEIGHT // 3))
        )

        mouse_pos = pygame.mouse.get_pos()
        color = (180, 140, 90) if self.button_rect.collidepoint(mouse_pos) else (120, 90, 50)

        pygame.draw.rect(self.screen, color, self.button_rect, border_radius=8)

        text = self.font_button.render("JUGAR", True, (30, 30, 30))
        self.screen.blit(
            text, text.get_rect(center=self.button_rect.center)
        )

    # -------------------------
    # DIBUJO JUEGO
    # -------------------------
    def draw_game(self):
        self.game_map.draw(self.screen)

        occupied_spots = [tower.rect.center for tower in self.towers]
        self.game_map.draw_tower_spots(self.screen, occupied_spots)

        for tower in self.towers:
            tower.draw(self.screen)

        for projectile in self.projectiles:
            projectile.draw(self.screen)

        for enemy in self.enemies:
            enemy.draw(self.screen)

        # HUD
        lives_text = self.font_hud.render(f"Vidas: {self.lives}", True, (255, 255, 255))
        gold_text = self.font_hud.render(f"Oro: {self.gold}", True, (255, 215, 0))

        self.screen.blit(lives_text, (10, 10))
        self.screen.blit(gold_text, (10, 40))

    # -------------------------
    # DIBUJO GAME OVER
    # -------------------------
    def draw_game_over(self):
        self.screen.fill((10, 10, 10))

        text = self.font_gameover.render(
            "GAME OVER", True, (180, 50, 50)
        )
        self.screen.blit(
            text, text.get_rect(center=(WIDTH // 2, HEIGHT // 3))
        )

        info = self.font_button.render(
            "Haz click para volver al menú", True, (200, 200, 200)
        )
        self.screen.blit(
            info, info.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        )

    # -------------------------
    # DIBUJO GENERAL
    # -------------------------
    def draw(self):
        if self.state == MENU:
            self.draw_menu()
        elif self.state == GAME:
            self.draw_game()
        elif self.state == GAME_OVER:
            self.draw_game_over()

        pygame.display.flip()
