import sys
import os
# ensure project root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pygame
from core.map import GameMap
from settings import HEIGHT
import math
import random

if __name__ == '__main__':
    pygame.init()
    # small hidden display so image loading and conversion works
    try:
        pygame.display.set_mode((1, 1))
    except Exception:
        pass
    random.seed(42)
    gm = GameMap()

    left_pts = []
    right_pts = []
    segments = 24
    for i in range(segments + 1):
        t = i / segments
        x = int(gm.bg_x + t * gm.map_width)
        left_y = int(HEIGHT * 0.30 + math.sin(t * 2 * math.pi) * HEIGHT * 0.03 + random.randint(-6, 6))
        right_y = int(HEIGHT * 0.70 + math.sin(t * 2 * math.pi + 1.1) * HEIGHT * 0.03 + random.randint(-6, 6))
        left_pts.append((x, left_y))
        right_pts.append((x, right_y))

    gm.path_left = left_pts
    gm.path_right = right_pts

    # recompute tower spots if available
    if hasattr(gm, 'recompute_tower_spots'):
        gm.recompute_tower_spots(n=8)
    else:
        spots = []
        for i in range(1, 9):
            x = int(gm.bg_x + i * (gm.map_width) / 9)
            y = int((left_pts[i * segments // 9][1] + right_pts[i * segments // 9][1]) // 2)
            spots.append((x, y))
        gm.tower_spots = spots
        gm.save_config()

    gm.save_config()
    print('Saved config to', gm.config_path)
    print('Left path sample:', gm.path_left[:3], '...')
    print('Right path sample:', gm.path_right[:3], '...')
    print('Tower spots:', gm.tower_spots)