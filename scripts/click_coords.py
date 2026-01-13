import pygame
import os
import sys
# ensure project root is on sys.path so 'settings' can be imported when running from scripts/
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from settings import WIDTH, HEIGHT

MAP_PATHS = [
    os.path.join('assets', 'imagenes', 'mapa', 'mapa.png'),
    os.path.join('assets', 'imagenes', 'mapa', 'mapa_principal.png')
]

def load_map_surface():
    for p in MAP_PATHS:
        if os.path.exists(p):
            try:
                img = pygame.image.load(p).convert()
                return img
            except Exception:
                pass
    return None


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption('Click-to-get-coords')
    font = pygame.font.SysFont(None, 20)

    img = load_map_surface()
    if img is None:
        print('No map image found in assets/imagenes/mapa/. Place mapa.png or mapa_principal.png there.')
        pygame.quit()
        return

    map_w, map_h = img.get_size()
    scale = HEIGHT / map_h
    map_width = int(map_w * scale)
    map_surf = pygame.transform.smoothscale(img, (map_width, HEIGHT))
    bg_x = (WIDTH - map_width) // 2

    last_click = None

    clock = pygame.time.Clock()
    running = True
    while running:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                running = False
            elif ev.type == pygame.MOUSEBUTTONDOWN:
                mx, my = ev.pos
                # convert to image coords if inside image area
                if bg_x <= mx < bg_x + map_width and 0 <= my < HEIGHT:
                    img_x = int((mx - bg_x) / map_width * map_w)
                    img_y = int(my / HEIGHT * map_h)
                    print(f'CLICK screen: ({mx}, {my})  image: ({img_x}, {img_y})')
                    last_click = (mx, my, img_x, img_y)
                else:
                    print(f'CLICK screen: ({mx}, {my}) (outside image)')
                    last_click = (mx, my, None, None)
            elif ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE or ev.key == pygame.K_q:
                    running = False

        screen.fill((0, 0, 0))
        screen.blit(map_surf, (bg_x, 0))

        # HUD
        y = 8
        lines = ['Click on the map to print coordinates to the terminal', 'ESC/Q to exit']
        for line in lines:
            screen.blit(font.render(line, True, (255, 255, 255)), (8, y))
            y += 20

        if last_click:
            mx, my, ix, iy = last_click
            text = f'Last click screen: ({mx}, {my})'
            if ix is not None:
                text += f'  image: ({ix}, {iy})'
            screen.blit(font.render(text, True, (255, 255, 0)), (8, y))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == '__main__':
    main()
