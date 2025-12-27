import pygame


class BuildMenu:
    def __init__(self, x, y, has_tower=False):
        self.font = pygame.font.SysFont("arial", 14)
        self.has_tower = has_tower

        self.archer_rect = pygame.Rect(x - 40, y - 70, 80, 30)
        self.cannon_rect = pygame.Rect(x - 40, y - 35, 80, 30)
        self.upgrade_rect = pygame.Rect(x - 40, y, 80, 30)

    def draw(self, screen):
        if not self.has_tower:
            pygame.draw.rect(screen, (60, 60, 60), self.archer_rect, border_radius=6)
            pygame.draw.rect(screen, (60, 60, 60), self.cannon_rect, border_radius=6)

            screen.blit(
                self.font.render("Mosquetero - 50", True, (255, 255, 255)),
                self.archer_rect.move(6, 6)
            )
            screen.blit(
                self.font.render("Cañón - 100", True, (255, 255, 255)),
                self.cannon_rect.move(6, 6)
            )
        else:
            pygame.draw.rect(screen, (90, 70, 40), self.upgrade_rect, border_radius=6)
            screen.blit(
                self.font.render("Mejorar - 75", True, (255, 255, 255)),
                self.upgrade_rect.move(6, 6)
            )

    def handle_click(self, pos):
        if not self.has_tower:
            if self.archer_rect.collidepoint(pos):
                return "archer"
            if self.cannon_rect.collidepoint(pos):
                return "cannon"
        else:
            if self.upgrade_rect.collidepoint(pos):
                return "upgrade"

        return None
