# Arquitectura Limpia: UI Pura vs Lógica del Juego

## Principio de Separación

La UI es completamente pura y no contiene lógica del juego. La UI solo:
- **Dibuja** elementos en pantalla
- **Detecta** clicks y eventos de entrada
- **Devuelve** eventos genéricos

La lógica del juego en `core/game.py` es la que:
- **Toma decisiones** basadas en eventos de la UI
- **Modifica el estado** del juego (crear torres, restar oro, etc.)
- **Genera datos** para que la UI muestre (opciones del menú, etc.)

## Ejemplo: Menú de Torres (BuildMenu)

### Antes (Acoplado)
```python
# UI tenía acceso a la lógica del juego
class BuildMenu:
    def __init__(self, x, y, has_tower=False, tower=None):
        # La UI accedía directamente a datos del juego
        refund = int(tower.total_cost / 2)
        if tower.level >= tower.max_level:  # Lógica del juego en UI
            self.options = [...]
```

**Problema**: La UI necesitaba saber sobre torres, niveles, costos, etc.

### Después (Puro)
```python
# UI solo recibe opciones ya preparadas
class BuildMenu:
    def __init__(self, x, y, options):
        """
        options: Lista de tuplas (key, label) genéricas
        Ejemplo: [("upgrade", "Mejorar - 75 oro"), ("sell", "Derribar - 50 oro")]
        """
        self.options = options  # Solo dibuja lo que le pasan
```

**Ventaja**: La UI es completamente agnóstica a la lógica del juego.

## Flujo Correcto

```
Usuario hace click
    ↓
BuildMenu.handle_click() devuelve la opción (ej: "upgrade")
    ↓
game.py recibe el evento y decide qué hacer
    ↓
game.py modifica estado (resta oro, sube nivel, etc.)
    ↓
game.py genera nuevas opciones para el menú
    ↓
BuildMenu.draw() dibuja las nuevas opciones
```

## Cómo game.py prepara las opciones

```python
# En handle_events()
for tower in self.towers:
    if tower.rect.collidepoint(event.pos):
        self.selected_tower = tower
        
        # Lógica del juego: Generar opciones basadas en estado
        options = []
        if tower.level >= tower.max_level:
            options.append(("max", "Nivel máximo"))
        else:
            options.append(("upgrade", f"Mejorar - {tower.upgrade_cost} oro"))
        
        refund = int(tower.total_cost / 2)
        options.append(("sell", f"Derribar - {refund} oro"))
        
        # Pasas las opciones ya preparadas a la UI
        self.build_menu = BuildMenu(tower.x, tower.y, options)
```

## Responsabilidades Claras

### BuildMenu (UI)
✅ Dibuja el menú
✅ Detecta clicks
✅ Devuelve evento ("archer", "upgrade", "sell", etc.)

### game.py (Lógica)
✅ Interpreta eventos de BuildMenu
✅ Valida si hay oro suficiente
✅ Crea torres o mejora existing
✅ Resta oro, modifica vidas
✅ Genera opciones para el próximo menú

## Ventajas de esta Arquitectura

1. **Testabilidad**: Puedes testear UI sin ejecutar lógica
2. **Reusabilidad**: BuildMenu puede usarse en otros proyectos
3. **Mantenibilidad**: Cambiar lógica del juego no afecta UI
4. **Debugging**: Errores claros: ¿Es UI o es lógica?
5. **Escalabilidad**: Fácil agregar nuevas torres sin tocar UI

