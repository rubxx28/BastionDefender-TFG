# UI Module - Interfaces del Juego

Este módulo contiene todas las interfaces visuales (screens) del juego, separadas de la lógica principal.

## Archivos

### `menu_screen.py` - MenuScreen
Pantalla del menú principal del juego.
- Muestra logo y título
- Botón para iniciar juego
- Animaciones de partículas
- Gestión de clicks en botón de inicio

**Uso:**
```python
from ui.menu_screen import MenuScreen
menu = MenuScreen()
menu.update()
menu.draw(screen)
if menu.handle_click(mouse_pos):
    # Iniciar juego
```

### `game_screen.py` - GameScreen
Pantalla del juego en progreso.
- Renderiza el mapa, torres, enemigos y proyectiles
- HUD con información del juego
- Mensajes de oleada
- Cuenta atrás entre oleadas

**Uso:**
```python
from ui.game_screen import GameScreen
game_screen = GameScreen()
game_screen.draw(screen, lives, gold, wave, countdown, show_countdown, 
                 enemies_spawned, enemies_to_spawn)
```

### `gameover_screen.py` - GameOverScreen
Pantalla de fin del juego.
- Muestra estadísticas finales (oleadas, oro gastado)
- Botones de reintentar y salir
- Animación de overlay oscuro

**Uso:**
```python
from ui.gameover_screen import GameOverScreen
game_over = GameOverScreen()
game_over.update()
result = game_over.handle_click(mouse_pos)  # "retry" o "exit"
game_over.draw(screen, waves_survived, gold_used)
```

### `tower_menu.py` - BuildMenu
Menú contextual para construir o mejorar torres.
- Muestra opciones dinámicas según posición
- Iconos de torres
- Información de costos
- Manejo de clicks

**Uso:**
```python
from ui.tower_menu import BuildMenu
build_menu = BuildMenu(x, y, has_tower=False, tower=None)
action = build_menu.handle_click(mouse_pos)  # "archer", "cannon", "magic", "upgrade", "sell"
build_menu.draw(screen)
```

### `hud.py` - HUD
Cabeza-up display (información en pantalla durante el juego).
- Vidas, oro, oleada actual
- Contador de enemigos
- Mensajes de oleada animados
- Cuenta atrás

**Uso:**
```python
from ui.hud import HUD
hud = HUD()
hud.draw(screen, lives, gold, wave, enemies_spawned, enemies_to_spawn)
hud.draw_wave_message(screen, "Oleada 1", message_timer)
hud.draw_countdown(screen, countdown)
```

## Estructura de Separación

```
ui/                      # Todas las interfaces visuales
├── menu_screen.py       # Pantalla de menú
├── game_screen.py       # Pantalla de juego
├── gameover_screen.py   # Pantalla de game over
├── tower_menu.py        # Menú de torres (contextual)
├── hud.py              # HUD durante el juego
└── __init__.py         # Exporta todas las clases
```

## Principios de Diseño

- **Separación de responsabilidades**: Cada archivo maneja una interfaz visual específica
- **Sin lógica de juego**: Las clases UI solo se encargan de renderizar y detectar clicks/eventos visuales
- **Reutilización**: Las clases se pueden instanciar múltiples veces si es necesario
- **Métodos simples**: `update()`, `draw()`, `handle_click()` son los métodos principales

## Integración con `core/game.py`

El archivo `core/game.py` debe instanciar estas clases y coordinar:
- Cambios de estado (MENU → GAME → GAME_OVER)
- Actualizaciones de datos
- Llamadas a `draw()` en el orden correcto

