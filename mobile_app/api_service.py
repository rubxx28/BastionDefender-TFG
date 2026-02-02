"""
Servicio para conectar con la API de BastionDefender
"""

import requests
from typing import List, Dict, Optional


class APIService:
    """Gestiona conexión con la API"""
    
    def __init__(self, base_url: str = "http://127.0.0.1:8000"):
        self.base_url = base_url
        self.timeout = 5
    
    def get_scores(self, player_id: int) -> Optional[List[Dict]]:
        """
        Obtener todas las puntuaciones de un jugador
        
        Args:
            player_id: ID del jugador a buscar
        
        Returns:
            Lista de diccionarios con datos de partidas, o None si hay error
        """
        try:
            url = f"{self.base_url}/scores/{player_id}"
            response = requests.get(url, timeout=self.timeout)
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                # No encontrado
                return []
            else:
                print(f"Error {response.status_code}: {response.text}")
                return None
        
        except requests.exceptions.Timeout:
            print("Timeout al conectar con el servidor")
            return None
        except requests.exceptions.ConnectionError:
            print("Error de conexión con el servidor")
            return None
        except Exception as e:
            print(f"Error inesperado: {e}")
            return None
