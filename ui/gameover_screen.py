import pygame
from settings import WIDTH, HEIGHT


class GameOverScreen:
    """Pantalla de Game Over"""
    
    def __init__(self):
        # Fuentes
        self.font_big = pygame.font.SysFont("arialblack", 64)
        self.font_button = pygame.font.SysFont("arial", 36)
        self.font_small = pygame.font.SysFont("arial", 20)
        
        # Botones
        self.retry_button_rect = pygame.Rect(
            WIDTH // 2 - 140, HEIGHT // 2 + 30, 120, 50)
        self.exit_button_rect = pygame.Rect(
            WIDTH // 2 + 20, HEIGHT // 2 + 30, 120, 50)
        
        # Animación
        self.alpha = 0
        self.particles = []
    
    def update(self):
        """Actualizar animación de Game Over"""
        if self.alpha < 200:
            self.alpha = min(self.alpha + 3, 200)
        
        # Actualizar partículas
        for p in self.particles[:]:
            p["life"] -= 1
            p["x"] += p["vx"]
            p["y"] += p["vy"]
            if p["life"] <= 0:
                self.particles.remove(p)
    
    def handle_click(self, pos):
        """Detectar clicks en botones"""
        if self.retry_button_rect.collidepoint(pos):
            return "retry"
        elif self.exit_button_rect.collidepoint(pos):
            return "exit"
        return None
    
    def draw(self, screen, waves_survived, gold_used):
        """Dibujar pantalla de Game Over"""
        # Overlay oscuro
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(self.alpha)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))
        
        # Título
        game_over_text = self.font_big.render("GAME OVER", True, (200, 50, 50))
        screen.blit(game_over_text, 
                   (WIDTH // 2 - game_over_text.get_width() // 2, 100))
        
        # Estadísticas
        stats_font = pygame.font.SysFont("arial", 28)
        waves_text = stats_font.render(f"Oleadas: {waves_survived}", True, (200, 200, 50))
        screen.blit(waves_text, 
                   (WIDTH // 2 - waves_text.get_width() // 2, 200))
        
        gold_text = stats_font.render(f"Oro gastado: {gold_used}", True, (200, 150, 50))
        screen.blit(gold_text, 
                   (WIDTH // 2 - gold_text.get_width() // 2, 250))
        
        # Botones
        mouse = pygame.mouse.get_pos()
        
        # Retry
        retry_hover = self.retry_button_rect.collidepoint(mouse)
        retry_color = (100, 200, 100) if retry_hover else (80, 150, 80)
        pygame.draw.rect(screen, retry_color, self.retry_button_rect, border_radius=10)
        pygame.draw.rect(screen, (150, 255, 150), self.retry_button_rect, 2, border_radius=10)
        retry_text = self.font_button.render("RETRY", True, (255, 255, 255))
        screen.blit(retry_text, 
                   (self.retry_button_rect.centerx - retry_text.get_width() // 2,
                    self.retry_button_rect.centery - retry_text.get_height() // 2))
        
        # Exit
        exit_hover = self.exit_button_rect.collidepoint(mouse)
        exit_color = (200, 100, 100) if exit_hover else (150, 80, 80)
        pygame.draw.rect(screen, exit_color, self.exit_button_rect, border_radius=10)
        pygame.draw.rect(screen, (255, 150, 150), self.exit_button_rect, 2, border_radius=10)
        exit_text = self.font_button.render("EXIT", True, (255, 255, 255))
        screen.blit(exit_text, 
                   (self.exit_button_rect.centerx - exit_text.get_width() // 2,
                    self.exit_button_rect.centery - exit_text.get_height() // 2))
