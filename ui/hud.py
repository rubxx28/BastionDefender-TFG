import pygame
from settings import WIDTH, HEIGHT


class HUD:
    """Cabeza-up display (interfaz en pantalla del juego)"""
    
    def __init__(self):
        self.font_hud = pygame.font.SysFont("arial", 22)
        self.font_wave = pygame.font.SysFont("arialblack", 40)
        self.font_countdown = pygame.font.SysFont("arialblack", 96)
        self.font_speed_button = pygame.font.SysFont("arial", 18, bold=True)
        self.font_id_small = pygame.font.SysFont("arial", 14)  # Fuente pequeña para ID
        self.max_lives = 10
        self.heart_size = 24
        
        # Botones de velocidad (esquina INFERIOR izquierda, estilo sutil)
        self.speed_button_size = 44
        self.speed_button_gap = 10
        self.speed_margin = 12
        left_x = 12
        # coordenada Y fija en base a la pantalla (inferior)
        self.speed_button_y = HEIGHT - self.speed_button_size - self.speed_margin

        # Botones: 0 = pausa, 1 = play, 2 = doble
        self.speed_buttons = {
            0: {"x": left_x, "color": (30, 30, 30, 180)},
            1: {"x": left_x + (self.speed_button_size + self.speed_button_gap) * 1, "color": (30, 30, 30, 180)},
            2: {"x": left_x + (self.speed_button_size + self.speed_button_gap) * 2, "color": (30, 30, 30, 180)}
        }
        self.current_speed = 1
    
    def draw_heart(self, screen, x, y, filled=True):
        """Dibujar un corazón bonito"""
        if filled:
            color = (255, 0, 0)
        else:
            color = (0, 0, 0)
        
        # Corazón usando dos círculos y un triángulo
        # Círculo izquierdo
        pygame.draw.circle(screen, color, (x - 4, y + 2), 5)
        # Círculo derecho
        pygame.draw.circle(screen, color, (x + 4, y + 2), 5)
        # Triángulo abajo
        pygame.draw.polygon(screen, color, [
            (x - 9, y + 2),
            (x + 9, y + 2),
            (x, y + 12)
        ])
    
    def draw(self, screen, lives, gold, wave, player_id=None):
        """Dibujar HUD del juego sin fondo"""
        # Dibujar corazones (10 en total)
        hearts_x = 20
        hearts_y = 18
        
        for i in range(self.max_lives):
            self.draw_heart(screen, hearts_x + i * 28, hearts_y, filled=(i < lives))
        
        # Oro (con sombra suave para mejor legibilidad)
        gold_text = self.font_hud.render(f"Oro: {gold}", True, (200, 150, 50))
        # Sombra
        shadow = self.font_hud.render(f"Oro: {gold}", True, (0, 0, 0))
        screen.blit(shadow, (WIDTH - 180, 18))
        screen.blit(gold_text, (WIDTH - 180, 15))
        
        # Oleada actual (con sombra)
        wave_text = self.font_hud.render(f"Oleada {wave}", True, (150, 200, 100))
        shadow = self.font_hud.render(f"Oleada {wave}", True, (0, 0, 0))
        screen.blit(shadow, (WIDTH // 2 - wave_text.get_width() // 2 + 1, 18))
        screen.blit(wave_text, (WIDTH // 2 - wave_text.get_width() // 2, 15))
        
        # Session ID (esquina inferior izquierda, a la derecha del botón x2)
        if player_id:
            id_text = self.font_id_small.render(f"ID: {player_id}", True, (120, 120, 120))
            id_x = 12 + (self.speed_button_size + self.speed_button_gap) * 3 + 8
            id_y = HEIGHT - 20
            screen.blit(id_text, (id_x, id_y))
        
        # Dibujar botones de velocidad
        self.draw_speed_buttons(screen)
    
    def draw_wave_message(self, screen, message, timer, max_timer=120):
        """Dibujar mensaje de oleada con animación"""
        if timer > 0:
            alpha = int(255 * (timer / max_timer)) if max_timer > 0 else 255
            # Color rojo brillante para minijefe, amarillo para oleadas normales
            if "MINIJEFE" in message:
                color = (255, 50, 50)  # Rojo brillante
            else:
                color = (255, 255, 100)  # Amarillo brillante
            msg_surf = self.font_wave.render(message, True, color)
            msg_surf.set_alpha(alpha)
            # Sombra negra para mejor legibilidad
            shadow_surf = self.font_wave.render(message, True, (0, 0, 0))
            shadow_surf.set_alpha(alpha // 2)
            screen.blit(shadow_surf, (WIDTH // 2 - msg_surf.get_width() // 2 + 3, 
                                     HEIGHT // 2 - 100 + 3))
            screen.blit(msg_surf, (WIDTH // 2 - msg_surf.get_width() // 2, 
                                  HEIGHT // 2 - 100))
    
    def draw_countdown(self, screen, countdown):
        """Dibujar cuenta atrás entre oleadas"""
        if countdown > 0:
            countdown_text = self.font_countdown.render(str(countdown), True, (255, 100, 100))
            countdown_text.set_alpha(255)
            # Sombra negra para mejor legibilidad
            shadow_text = self.font_countdown.render(str(countdown), True, (0, 0, 0))
            shadow_text.set_alpha(100)
            screen.blit(shadow_text, 
                       (WIDTH // 2 - countdown_text.get_width() // 2 + 4,
                        HEIGHT // 2 - countdown_text.get_height() // 2 + 4))
            screen.blit(countdown_text, 
                       (WIDTH // 2 - countdown_text.get_width() // 2,
                        HEIGHT // 2 - countdown_text.get_height() // 2))

    def draw_speed_buttons(self, screen):
        """Dibujar botones de control de velocidad"""
        mouse = pygame.mouse.get_pos()

        for speed, button_info in self.speed_buttons.items():
            x = button_info["x"]
            y = self.speed_button_y
            size = self.speed_button_size
            rect = pygame.Rect(x, y, size, size)

            # Surface para fondo semi-transparente con borde redondeado
            surf = pygame.Surface((size, size), pygame.SRCALPHA)
            bg_color = button_info.get("color", (30, 30, 30, 180))

            is_hovered = rect.collidepoint(mouse)
            border_color = (200, 200, 200, 180) if speed == self.current_speed else (120, 120, 120, 150)

            # Aumentar alpha o brillo al hacer hover
            if is_hovered:
                bg_color = (bg_color[0], bg_color[1], bg_color[2], min(255, bg_color[3] + 40))

            pygame.draw.rect(surf, bg_color, (0, 0, size, size), border_radius=10)
            pygame.draw.rect(surf, border_color, (1, 1, size-2, size-2), 1, border_radius=10)

            # Dibujar iconos (blanco) en el centro
            cx, cy = size // 2, size // 2
            icon_color = (245, 245, 245)

            if speed == 1:
                # Play: triángulo
                tri = [
                    (cx - 8, cy - 12),
                    (cx - 8, cy + 12),
                    (cx + 12, cy)
                ]
                pygame.draw.polygon(surf, icon_color, tri)
            elif speed == 0:
                # Pause: dos rectángulos
                w = 6
                h = 20
                pygame.draw.rect(surf, icon_color, (cx - 9, cy - h//2, w, h), border_radius=2)
                pygame.draw.rect(surf, icon_color, (cx + 3, cy - h//2, w, h), border_radius=2)
            else:
                # Double-play: dos triángulos pequeños
                tri1 = [
                    (cx - 14, cy - 12),
                    (cx - 14, cy + 12),
                    (cx - 2, cy)
                ]
                tri2 = [
                    (cx - 2, cy - 12),
                    (cx - 2, cy + 12),
                    (cx + 12, cy)
                ]
                pygame.draw.polygon(surf, icon_color, tri1)
                pygame.draw.polygon(surf, icon_color, tri2)

            screen.blit(surf, (x, y))

    def get_speed_button_clicked(self, mouse_pos):
        """Retornar la velocidad del botón clickeado, o None si no hay click"""
        for speed, button_info in self.speed_buttons.items():
            x = button_info["x"]
            y = self.speed_button_y
            size = self.speed_button_size
            rect = pygame.Rect(x, y, size, size)
            if rect.collidepoint(mouse_pos):
                self.current_speed = speed
                return speed
        return None

    def set_current_speed(self, speed):
        """Actualizar el indicador de velocidad actual"""
        if speed in (0, 1, 2):
            self.current_speed = speed
