import pygame
import threading
import uvicorn
from core.game import Game

def run_api():
    """Inicia la API en un hilo separado"""
    uvicorn.run("api.main:app", host="127.0.0.1", port=8000, log_level="info")

def main():
    # Iniciar la API en un hilo separado
    api_thread = threading.Thread(target=run_api, daemon=True)
    api_thread.start()
    print("API iniciada en http://127.0.0.1:8000")
    
    # Iniciar el juego
    pygame.init()
    game = Game()
    game.run()
    pygame.quit()

if __name__ == "__main__":
    main()
