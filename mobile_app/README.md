# Bastion Defender - Aplicación Móvil

App Kivy para consultar el historial de partidas usando tu Session ID.

## Instalación

```bash
pip install -r ../requirements.txt
```

## Ejecución

```bash
python main.py
```

## Funcionalidad

1. **Búsqueda**: Ingresa tu Session ID (6 dígitos) que obtuviste cuando jugaste
2. **Resultados**: Ve tu historial completo con:
   - Número de oleadas alcanzadas
   - Duración de cada partida
   - Fecha de juego
   - Estadísticas generales (partidas totales, oleada promedio, tiempo total)

## Archivos

- `main.py` - App principal con dos pantallas (búsqueda y resultados)
- `api_service.py` - Servicio para conectar con la API de Bastion Defender
