import pygame
from settings import WIDTH, HEIGHT


class MenuScreen:
    """Pantalla del menú principal"""
    
    def __init__(self):
        # Fuentes
        self.font_title = pygame.font.SysFont("arialblack", 72)
        self.font_button = pygame.font.SysFont("arial", 36)
        
        # Botón de inicio
        self.button_rect = pygame.Rect(
            WIDTH // 2 - 160, HEIGHT // 2 + 40, 320, 70)
        
        # Visuals de portada
        self.menu_bg = None
        self.logo = None
        self._load_assets()
        
        # Animación
        self.menu_pulse = 0.0
        self.menu_particles = []
        self.menu_particle_timer = 0
    
    def _load_assets(self):
        """Cargar imágenes y recursos"""
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
    
    def update(self):
        """Actualizar animaciones de menú"""
        self.menu_pulse = (self.menu_pulse + 0.05) % (2 * 3.14159)
        self.menu_particle_timer += 1
        
        if self.menu_particle_timer >= 10:
            import random
            particle = {
                "x": random.randint(0, WIDTH),
                "y": random.randint(0, HEIGHT),
                "vx": random.uniform(-1, 1),
                "vy": random.uniform(-2, -0.5),
                "life": 60,
                "max_life": 60
            }
            self.menu_particles.append(particle)
            self.menu_particle_timer = 0
        
        # Actualizar partículas
        for p in self.menu_particles[:]:
            p["life"] -= 1
            p["x"] += p["vx"]
            p["y"] += p["vy"]
            if p["life"] <= 0:
                self.menu_particles.remove(p)
    
    def handle_click(self, pos):
        """Detectar click en botón de inicio"""
        return self.button_rect.collidepoint(pos)
    
    def draw(self, screen):
        """Dibujar pantalla del menú"""
        # Fondo
        if self.menu_bg:
            screen.blit(self.menu_bg, (0, 0))
        else:
            screen.fill((20, 20, 30))
        
        # Dibujar partículas
        for p in self.menu_particles:
            alpha = int(255 * (p["life"] / p["max_life"]))
            color = (100 + alpha // 2, 150, 200)
            pygame.draw.circle(screen, color, (int(p["x"]), int(p["y"])), 2)
        
        # Logo
        if self.logo:
            logo_rect = self.logo.get_rect(center=(WIDTH // 2, HEIGHT // 3))
            screen.blit(self.logo, logo_rect)
        
        # Título
        title = self.font_title.render("BASTION DEFENDER", True, (200, 150, 50))
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 80))
        
        # Botón con animación
        pulse = 1.0 + 0.1 * (0.5 * (1 + pygame.math.Vector2(1, 0).dot(
            pygame.math.Vector2(1, 0))))
        
        button_color = (150 + int(50 * (1 + pygame.math.Vector2(1, 0).dot(
            pygame.math.Vector2(1, 0)))), 100, 50)
        pygame.draw.rect(screen, button_color, self.button_rect, border_radius=15)
        pygame.draw.rect(screen, (200, 150, 100), self.button_rect, 3, border_radius=15)
        
        button_text = self.font_button.render("PLAY", True, (255, 255, 255))
        screen.blit(button_text, (WIDTH // 2 - button_text.get_width() // 2, 
                                   self.button_rect.centery - button_text.get_height() // 2))
