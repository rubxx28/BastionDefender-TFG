import pygame
from settings import WIDTH, HEIGHT


class MenuScreen:
    """Pantalla del menú principal con imagen de fondo"""
    
    def __init__(self):
        # Fuentes
        self.font_button = pygame.font.SysFont("arial", 36, bold=True)
        
        # Botón de inicio (más abajo)
        self.button_rect = pygame.Rect(
            WIDTH // 2 - 160, HEIGHT - 80, 320, 70)
        self.button_hovered = False
        
        # Imagen de fondo
        self.menu_bg = None
        self._load_assets()
        
        # Animación
        self.time = 0.0
    
    def _load_assets(self):
        """Cargar imagen de fondo"""
        try:
            self.menu_bg = pygame.image.load(
                "assets/imagenes/portada/portada.png").convert()
            self.menu_bg = pygame.transform.smoothscale(
                self.menu_bg, (WIDTH, HEIGHT))
        except Exception:
            self.menu_bg = None
    
    def update(self):
        """Actualizar animaciones de menú"""
        self.time += 0.016  # ~60 FPS
    
    def handle_click(self, pos):
        """Detectar click en botón de inicio"""
        return self.button_rect.collidepoint(pos)
    
    def handle_hover(self, pos):
        """Detectar si el mouse está sobre el botón"""
        self.button_hovered = self.button_rect.collidepoint(pos)
    
    def draw(self, screen):
        """Dibujar pantalla del menú"""
        # Fondo
        if self.menu_bg:
            screen.blit(self.menu_bg, (0, 0))
        else:
            # Fondo por defecto si no hay imagen
            screen.fill((30, 50, 80))
        
        # Botón JUGAR con animación
        if self.button_hovered:
            button_color = (180, 120, 50)  # Dorado brillante
            button_outline = (220, 160, 80)
        else:
            button_color = (140, 90, 30)  # Marrón dorado
            button_outline = (180, 120, 50)
        
        # Efecto de glow al pasar el mouse
        if self.button_hovered:
            glow_surface = pygame.Surface((self.button_rect.width + 20, 
                                          self.button_rect.height + 20), 
                                         pygame.SRCALPHA)
            pygame.draw.rect(glow_surface, (180, 120, 50, 60),
                            glow_surface.get_rect(), border_radius=20)
            screen.blit(glow_surface, (self.button_rect.x - 10, self.button_rect.y - 10))
        
        pygame.draw.rect(screen, button_color, self.button_rect, border_radius=15)
        pygame.draw.rect(screen, button_outline, self.button_rect, 3, border_radius=15)
        
        button_text = self.font_button.render("JUGAR", True, (255, 255, 255))
        screen.blit(button_text, (WIDTH // 2 - button_text.get_width() // 2, 
                                   self.button_rect.centery - button_text.get_height() // 2))
