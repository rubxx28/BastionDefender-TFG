import pygame
from settings import WIDTH, HEIGHT, FPS
from core.map import GameMap
from entities.enemy import Enemy

# Estados del juego
MENU = "menu"
GAME = "game"


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

        # Botón menú
        self.button_rect = pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2, 300, 70)

        self.reset_game()

    # -------------------------
    # RESET DEL JUEGO
    # -------------------------
    def reset_game(self):
        self.game_map = GameMap()
        self.enemies = []

        self.spawn_timer = 0
        self.spawn_delay = 120  # frames entre enemigos

        self.lives = 10
        self.wave = 1

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

    # -------------------------
    # UPDATE
    # -------------------------
    def update(self):
        if self.state != GAME:
            return

        # Spawn de enemigos
        self.spawn_timer += 1
        if self.spawn_timer >= self.spawn_delay:
            self.enemies.append(Enemy(self.game_map.get_path()))

            self.spawn_timer = 0

        # Actualizar enemigos
        for enemy in self.enemies[:]:
            enemy.update()
            if not enemy.alive:
                self.enemies.remove(enemy)
                self.lives -= 1

        # Game Over → volver al menú
        if self.lives <= 0:
            self.state = MENU

    # -------------------------
    # DIBUJO MENU
    # -------------------------
    def draw_menu(self):
        self.screen.fill((34, 139, 34))

        title = self.font_title.render(
            "Bastion Defender", True, (139, 69, 19)
        )
        self.screen.blit(
            title, title.get_rect(center=(WIDTH // 2, HEIGHT // 3))
        )

        pygame.draw.rect(self.screen, (139, 69, 19), self.button_rect)
        text = self.font_button.render("JUGAR", True, (255, 255, 255))
        self.screen.blit(
            text, text.get_rect(center=self.button_rect.center)
        )

    # -------------------------
    # DIBUJO JUEGO
    # -------------------------
    def draw_game(self):
        self.game_map.draw(self.screen)

        for enemy in self.enemies:
            enemy.draw(self.screen)

        # HUD básico
        lives_text = self.font_hud.render(
            f"Vidas: {self.lives}", True, (255, 255, 255)
        )
        self.screen.blit(lives_text, (10, 10))

    # -------------------------
    # DIBUJO GENERAL
    # -------------------------
    def draw(self):
        if self.state == MENU:
            self.draw_menu()
        elif self.state == GAME:
            self.draw_game()

        pygame.display.flip()
