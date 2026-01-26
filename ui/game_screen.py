import pygame
from settings import WIDTH, HEIGHT


class GameScreen:
    """Pantalla principal del juego en progreso"""
    
    def __init__(self):
        # Fuentes para HUD
        self.font_hud = pygame.font.SysFont("arial", 22)
        self.font_wave = pygame.font.SysFont("arialblack", 40)
        self.font_countdown = pygame.font.SysFont("arialblack", 96)
        
        # Área del HUD
        self.hud_height = 60
        self.hud_rect = pygame.Rect(0, 0, WIDTH, self.hud_height)
        
        # Animación de mensaje de oleada
        self.wave_message = ""
        self.wave_message_timer = 0
    
    def update(self, lives, gold, wave, countdown, show_countdown):
        """Actualizar estado del HUD"""
        if self.wave_message_timer > 0:
            self.wave_message_timer -= 1
    
    def set_wave_message(self, message, duration=120):
        """Establecer mensaje de oleada"""
        self.wave_message = message
        self.wave_message_timer = duration
    
    def draw(self, screen, lives, gold, wave, countdown, show_countdown, 
             enemies_spawned, enemies_to_spawn):
        """Dibujar HUD del juego"""
        # Fondo del HUD
        pygame.draw.rect(screen, (30, 25, 15), self.hud_rect)
        pygame.draw.line(screen, (100, 80, 40), (0, self.hud_height),
                        (WIDTH, self.hud_height), 2)
        
        # Vidas
        lives_text = self.font_hud.render(f"❤ {lives}", True, (200, 50, 50))
        screen.blit(lives_text, (20, 15))
        
        # Oro
        gold_text = self.font_hud.render(f"💰 {gold}", True, (200, 150, 50))
        screen.blit(gold_text, (200, 15))
        
        # Oleada actual
        wave_text = self.font_hud.render(f"Oleada {wave}", True, (150, 200, 100))
        screen.blit(wave_text, (420, 15))
        
        # Enemigos restantes
        enemies_text = self.font_hud.render(
            f"Enemigos: {enemies_spawned}/{enemies_to_spawn}", True, (150, 150, 200))
        screen.blit(enemies_text, (650, 15))
        
        # Mensaje de oleada (si está activo)
        if self.wave_message_timer > 0:
            alpha = int(255 * (self.wave_message_timer / 120)) if self.wave_message_timer > 0 else 0
            msg_surf = self.font_wave.render(self.wave_message, True, (200, 200, 50))
            msg_surf.set_alpha(alpha)
            screen.blit(msg_surf, (WIDTH // 2 - msg_surf.get_width() // 2, 
                                  HEIGHT // 2 - 100))
        
        # Cuenta atrás entre oleadas
        if show_countdown and countdown > 0:
            countdown_text = self.font_countdown.render(str(countdown), True, (255, 200, 100))
            countdown_text.set_alpha(200)
            screen.blit(countdown_text, 
                       (WIDTH // 2 - countdown_text.get_width() // 2,
                        HEIGHT // 2 - countdown_text.get_height() // 2))
    
    def draw_map_and_entities(self, screen, game_map, towers, enemies, projectiles):
        """Dibujar mapa, torres, enemigos y proyectiles"""
        # Dibujar mapa
        game_map.draw(screen)
        
        # Dibujar torres
        for tower in towers:
            tower.draw(screen)
        
        # Dibujar enemigos
        for enemy in enemies:
            enemy.draw(screen)
        
        # Dibujar proyectiles
        for projectile in projectiles:
            projectile.draw(screen)
