import pygame


class BuildMenu:
    ICONS = {}  # cache de iconos por tipo

    def __init__(self, x, y, has_tower=False, tower=None):
        self.x = x
        self.y = y
        self.has_tower = has_tower
        self.tower = tower

        # Fuente más compacta y limpia
        self.font = pygame.font.SysFont("arial", 14)
        self.icon_size = 30

        # Opciones dinámicas (si hay torre, comprobar nivel máximo)
        if has_tower:
            refund = int(tower.total_cost / 2) if tower else 0
            if tower and tower.level >= tower.max_level:
                self.options = [
                    ("max", "Nivel máximo"),
                    ("sell", f"Derribar - {refund} oro")
                ]
            else:
                self.options = [
                    ("upgrade",
                     f"Mejorar - {tower.upgrade_cost if tower else 75} oro"),
                    ("sell", f"Derribar - {refund} oro")
                ]
        else:
            self.options = [
                ("archer", "Mosqueteros - 50 oro"),
                ("cannon", "Cañón - 100 oro"),
                ("magic", "Mago - 150 oro")
            ]

        # Dimensiones agradables y compactas
        self.option_height = 44
        self.width = 220
        self.height = self.option_height * len(self.options) + 16

        self.rect = pygame.Rect(
            self.x + 30,
            self.y - self.height // 2,
            self.width,
            self.height
        )

        # Rects individuales de botones
        self.buttons = []
        for i, (key, _) in enumerate(self.options):
            r = pygame.Rect(
                self.rect.x + 8,
                self.rect.y + 8 + i * self.option_height,
                self.width - 16,
                self.option_height - 8
            )
            self.buttons.append((key, r))

        # Cargar iconos (si existen)
        self._load_icons()

    def _load_icons(self):
        mapping = {
            "archer": "assets/imagenes/towers/mosquetera1.png",
            "cannon": "assets/imagenes/towers/cañon1.png",
            "magic": "assets/imagenes/towers/magica1.png",
        }
        for key, path in mapping.items():
            if key not in BuildMenu.ICONS:
                try:
                    img = pygame.image.load(path).convert_alpha()
                    img = pygame.transform.smoothscale(
                        img, (self.icon_size, self.icon_size))
                    BuildMenu.ICONS[key] = img
                except Exception:
                    BuildMenu.ICONS[key] = None  # no hay icono disponible

    def handle_click(self, pos):
        for key, rect in self.buttons:
            if rect.collidepoint(pos):
                # "max" no hace nada
                if key == "max":
                    return None
                return key
        return None

    def get_hover(self, mouse_pos):

        for key, rect in self.buttons:
            if rect.collidepoint(mouse_pos):
                return key
        return None

    def draw(self, screen):
        # Sombra (superficie con alpha)
        shadow = pygame.Surface(
            (self.width + 8, self.height + 8), pygame.SRCALPHA)
        shadow.fill((0, 0, 0, 110))
        screen.blit(shadow, (self.rect.x - 4, self.rect.y - 4))

        # Panel exterior (madera oscura) y panel interior (parchment)
        pygame.draw.rect(screen, (60, 45, 25), self.rect, border_radius=10)
        inner = self.rect.inflate(-6, -6)
        pygame.draw.rect(screen, (200, 170, 110), inner, border_radius=8)
        pygame.draw.rect(screen, (120, 90, 50), inner, 2, border_radius=8)

        # Mostrar nivel en el menú si hay torre asociada
        if self.tower:
            small_font = pygame.font.SysFont("arial", 12)
            level_text = f"Nivel {self.tower.level}"
            label = small_font.render(level_text, True, (80, 50, 20))
            badge_rect = pygame.Rect(inner.right - 8 - 44, inner.y + 8, 44, 20)
            pygame.draw.rect(screen, (120, 90, 50),
                             badge_rect, border_radius=6)
            inner_bad = badge_rect.inflate(-4, -4)
            pygame.draw.rect(screen, (200, 170, 110),
                             inner_bad, border_radius=5)
            screen.blit(label, (inner_bad.centerx - label.get_width() //
                        2, inner_bad.centery - label.get_height() // 2))

        mouse = pygame.mouse.get_pos()

        # Dibujar opciones
        for ((key, text), (_, rect)) in zip(self.options, self.buttons):
            hover = rect.collidepoint(mouse) if key != "max" else False

            # Fondo de opción (más claro al hacer hover)
            if key == "max":
                bg = (140, 140, 140)  # tono deshabilitado
            else:
                bg = (200, 180, 130) if hover else (160, 140, 100)
            pygame.draw.rect(screen, bg, rect, border_radius=6)

            # Icono a la izquierda
            icon_x = rect.x + 8
            icon_y = rect.y + (rect.height - self.icon_size) // 2

            if key == "upgrade":
                center = (icon_x + self.icon_size //
                          2, rect.y + rect.height // 2)
                pygame.draw.circle(screen, (220, 200, 120),
                                   center, self.icon_size // 2)
                plus = self.font.render("+", True, (80, 50, 20))
                screen.blit(plus, plus.get_rect(center=center))
            elif key == "max":
                lock_w = self.icon_size - 12
                lock_h = self.icon_size - 20
                lock_x = icon_x + 6
                lock_y = icon_y + 10
                pygame.draw.rect(
                    screen, (100, 100, 100), (lock_x, lock_y, lock_w, lock_h), border_radius=3)
                pygame.draw.circle(screen, (100, 100, 100),
                                   (icon_x + self.icon_size // 2, icon_y + 8), 6)
            elif key == "sell":
                center = (icon_x + self.icon_size //
                          2, rect.y + rect.height // 2)
                pygame.draw.circle(screen, (230, 190, 60),
                                   center, self.icon_size // 2)
                coin = self.font.render("O", True, (80, 50, 20))
                screen.blit(coin, coin.get_rect(center=center))
            else:
                icon = BuildMenu.ICONS.get(key)
                if icon:
                    screen.blit(icon, (icon_x, icon_y))
                else:
                    pygame.draw.rect(screen, (120, 120, 120), (icon_x, icon_y,
                                     self.icon_size, self.icon_size), border_radius=4)

            # Texto (inversión de color si hover para mejor legibilidad)
            if key == "max":
                label_color = (80, 80, 80)
            else:
                label_color = (40, 30, 20) if hover else (25, 25, 25)

            label = self.font.render(text, True, label_color)
            text_x = icon_x + self.icon_size + 12
            text_y = rect.y + rect.height // 2 - label.get_height() // 2
            screen.blit(label, (text_x, text_y))
