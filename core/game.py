import pygame
from settings import WIDTH, HEIGHT, FPS
from core.map import GameMap
from entities.enemy import Enemy

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Bastion Defender")
        self.clock = pygame.time.Clock()
        self.running = True

        self.game_map = GameMap()
        self.enemies = []

        self.spawn_timer = 0
        self.spawn_delay = 120  # frames (2 segundos)

        self.lives = 10

    def run(self):
        while self.running:
            self.clock.tick(FPS)
            self.handle_events()
            self.update()
            self.draw()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

    def update(self):
        # Spawner infinito
        self.spawn_timer += 1
        if self.spawn_timer >= self.spawn_delay:
            self.enemies.append(Enemy(self.game_map.get_path()))
            self.spawn_timer = 0

        for enemy in self.enemies[:]:
            enemy.update()
            if not enemy.alive:
                self.enemies.remove(enemy)
                self.lives -= 1

        if self.lives <= 0:
            self.running = False

    def draw(self):
        self.game_map.draw(self.screen)

        for enemy in self.enemies:
            enemy.draw(self.screen)

        pygame.display.flip()
