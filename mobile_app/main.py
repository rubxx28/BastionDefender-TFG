"""
BastionDefender Mobile App - Kivy
Busca tu ID de sesión para ver tu historial de partidas
"""

from kivy.app import App
from kivy.uix.screenmanager import Screen, ScreenManager, FadeTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle, RoundedRectangle, Line
import requests
import threading
import uvicorn
import sys
import os
from api_service import APIService

# Agregar el directorio padre al path para poder importar api
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Tamaño ventana
Window.size = (400, 700)

# Colores temáticos (Medieval/Fantasy)
COLOR_PRIMARY = (0.2, 0.4, 0.6, 1)      # Azul oscuro
COLOR_SECONDARY = (0.9, 0.7, 0.2, 1)    # Dorado
COLOR_ACCENT = (0.8, 0.2, 0.2, 1)       # Rojo
COLOR_BACKGROUND = (0.15, 0.15, 0.2, 1) # Gris oscuro
COLOR_TEXT = (1, 1, 1, 1)               # Blanco
COLOR_SUCCESS = (0.2, 0.7, 0.2, 1)      # Verde


def run_api():
    """Inicia la API en un hilo separado"""
    uvicorn.run("api.main:app", host="127.0.0.1", port=8000, log_level="info")


class RoundedButton(Button):
    """Botón con esquinas redondeadas"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_color = (0, 0, 0, 0)
        self.bind(size=self._update_canvas)
    
    def _update_canvas(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*COLOR_SECONDARY)
            RoundedRectangle(
                size=self.size,
                pos=self.pos,
                radius=[15]
            )


class SearchScreen(Screen):
    """Pantalla de búsqueda por ID de sesión"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.api_service = APIService()
        self.name = "search"
        
        # Fondo
        with self.canvas.before:
            Color(*COLOR_BACKGROUND)
            self.bg_rect = Rectangle(size=self.size, pos=self.pos)
            self.bind(size=self._update_bg, pos=self._update_bg)
        
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        # Título
        title_layout = BoxLayout(orientation='vertical', size_hint_y=0.25, spacing=10)
        
        title = Label(
            text='BASTION DEFENDER',
            markup=True,
            size_hint_y=0.5,
            font_size='28sp',
            bold=True,
            color=COLOR_SECONDARY
        )
        title_layout.add_widget(title)
        
        subtitle = Label(
            text='Consulta tu Historial de Batalla',
            size_hint_y=0.5,
            font_size='16sp',
            color=(0.8, 0.8, 0.8, 1)
        )
        title_layout.add_widget(subtitle)
        layout.add_widget(title_layout)
        
        # Instrucción con estilo
        instruction = Label(
            text='Ingresa tu Session ID para ver tus batallas',
            markup=True,
            size_hint_y=0.1,
            font_size='13sp',
            color=(0.9, 0.9, 0.9, 1)
        )
        layout.add_widget(instruction)
        
        # Campo de búsqueda
        self.search_input = TextInput(
            multiline=False,
            hint_text='Ingresa tu ID (6 digitos)',
            input_filter='int',
            size_hint_y=0.15,
            font_size='20sp',
            padding=[10, 10]
        )
        layout.add_widget(self.search_input)
        
        # Botón buscar mejorado
        search_btn = RoundedButton(
            text='BUSCAR REGISTRO',
            size_hint_y=0.12,
            font_size='16sp',
            bold=True,
            color=COLOR_BACKGROUND
        )
        search_btn.bind(on_press=self.on_search)
        layout.add_widget(search_btn)
        
        # Espacio
        layout.add_widget(Label(size_hint_y=0.35))
        
        # Footer con info
        footer = Label(
            text='[b]¿Cómo obtener tu ID?[/b]\nAparece al final de cada partida en Bastion Defender',
            markup=True,
            size_hint_y=0.15,
            font_size='11sp',
            color=(0.7, 0.7, 0.7, 1)
        )
        layout.add_widget(footer)
        
        self.add_widget(layout)
    
    def _update_bg(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size
    
    def on_search(self, instance):
        """Validar entrada y buscar"""
        player_id = self.search_input.text.strip()
        
        if not player_id:
            self.show_error("Ingresa un ID valido")
            return
        
        try:
            player_id_int = int(player_id)
        except ValueError:
            self.show_error("El ID debe ser un numero")
            return
        
        # Cambiar a pantalla de carga
        self.show_loading()
        
        # Hacer búsqueda en background
        Clock.schedule_once(
            lambda dt: self.fetch_results(player_id_int),
            0.1
        )
    
    def fetch_results(self, player_id):
        """Obtener resultados de la API"""
        try:
            results = self.api_service.get_scores(player_id)
            self.hide_loading()
            
            if results is None:
                self.show_error("Error al conectar con el servidor")
                return
            
            if not results:
                self.show_error(f"No se encontraron partidas\npara ID {player_id}")
                return
            
            # Ir a pantalla de resultados
            results_screen = self.manager.get_screen('results')
            results_screen.set_data(player_id, results)
            self.manager.current = 'results'
            
        except Exception as e:
            self.hide_loading()
            self.show_error(f"Error: {str(e)}")
    
    def show_loading(self):
        """Mostrar popup de carga"""
        content = BoxLayout(orientation='vertical', padding=20, spacing=20)
        content.add_widget(Label(text='Buscando...', font_size='18sp'))
        
        popup = Popup(
            title='Cargando',
            content=content,
            size_hint=(0.6, 0.2)
        )
        popup.open()
        self.loading_popup = popup
    
    def hide_loading(self):
        """Ocultar popup de carga"""
        if hasattr(self, 'loading_popup'):
            self.loading_popup.dismiss()
    
    def show_error(self, message):
        """Mostrar popup de error"""
        content = BoxLayout(orientation='vertical', padding=20, spacing=20)
        content.add_widget(Label(text=message, font_size='14sp'))
        
        close_btn = Button(
            text='OK',
            size_hint_y=0.3,
            background_normal='',
            background_color=COLOR_ACCENT
        )
        content.add_widget(close_btn)
        
        popup = Popup(
            title='Error',
            content=content,
            size_hint=(0.85, 0.35)
        )
        close_btn.bind(on_press=popup.dismiss)
        popup.open()


class ResultsScreen(Screen):
    """Pantalla que muestra el historial de partidas"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "results"
        
        # Fondo
        with self.canvas.before:
            Color(*COLOR_BACKGROUND)
            self.bg_rect = Rectangle(size=self.size, pos=self.pos)
            self.bind(size=self._update_bg, pos=self._update_bg)
        
        self.layout = BoxLayout(orientation='vertical', padding=15, spacing=15)
        self.add_widget(self.layout)
    
    def _update_bg(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size
    
    def set_data(self, player_id, results):
        """Cargar datos de resultados"""
        self.layout.clear_widgets()
        
        # Encabezado
        header = BoxLayout(orientation='horizontal', size_hint_y=0.08, spacing=15)
        
        title_box = BoxLayout(orientation='vertical', size_hint_x=0.7)
        title_box.add_widget(Label(
            text='HISTORIAL DE BATALLA',
            bold=True,
            font_size='16sp',
            color=COLOR_SECONDARY,
            size_hint_y=0.5
        ))
        title_box.add_widget(Label(
            text=f'ID: {player_id}',
            font_size='14sp',
            color=(0.9, 0.9, 0.9, 1),
            size_hint_y=0.5
        ))
        header.add_widget(title_box)
        
        back_btn = Button(
            text='Volver',
            size_hint_x=0.3,
            background_normal='',
            background_color=COLOR_ACCENT,
            font_size='12sp'
        )
        back_btn.bind(on_press=self.go_back)
        header.add_widget(back_btn)
        self.layout.add_widget(header)
        
        # Estadísticas generales
        total_waves = sum(r['waves'] for r in results)
        total_duration = sum(r['duration_seconds'] for r in results)
        avg_waves = total_waves / len(results) if results else 0
        max_waves = max((r['waves'] for r in results), default=0)
        
        stats_text = f"Partidas: {len(results)} | Oleadas: {total_waves} | Promedio: {avg_waves:.1f} | Max: {max_waves}"
        
        stats_label = Label(
            text=stats_text,
            size_hint_y=0.08,
            font_size='13sp',
            color=COLOR_SECONDARY
        )
        self.layout.add_widget(stats_label)
        
        # Línea separadora
        sep = Widget(size_hint_y=0.01)
        with sep.canvas:
            Color(0.5, 0.5, 0.5, 0.3)
            Line(points=[0, 0, Window.width, 0], width=1)
        self.layout.add_widget(sep)
        
        # Lista de partidas
        scroll = ScrollView(size_hint_y=0.7)
        games_list = GridLayout(cols=1, spacing=10, size_hint_y=None, padding=[5, 5])
        games_list.bind(minimum_height=games_list.setter('height'))
        
        for i, result in enumerate(sorted(results, key=lambda x: x.get('played_at', ''), reverse=True), 1):
            game_item = self._create_game_item(i, result)
            games_list.add_widget(game_item)
        
        scroll.add_widget(games_list)
        self.layout.add_widget(scroll)
    
    def _create_game_item(self, index, result):
        """Crear widget para una partida"""
        waves = result.get('waves', 0)
        duration = result.get('duration_seconds', 0)
        played_at = result.get('played_at', 'N/A')
        
        # Simplificar fecha
        if 'T' in str(played_at):
            played_at = str(played_at).split('T')[0]
        
        # Prefijo según oleadas
        if waves >= 50:
            wave_prefix = '[G.O.A.T.]'
        elif waves >= 40:
            wave_prefix = '[IMMORTAL]'
        elif waves >= 30:
            wave_prefix = '[SUPREME]'
        elif waves >= 20:
            wave_prefix = '[MASTER]'
        elif waves >= 15:
            wave_prefix = '[LEGENDARY]'
        elif waves >= 10:
            wave_prefix = '[EPIC]'
        elif waves >= 5:
            wave_prefix = '[GOOD]'
        else:
            wave_prefix = ''
        
        item = BoxLayout(orientation='vertical', size_hint_y=None, height=85, padding=[10, 10], spacing=5)
        
        # Fondo del item
        with item.canvas.before:
            Color(0.25, 0.25, 0.3, 0.8)
            item_bg = RoundedRectangle(
                size=item.size,
                pos=item.pos,
                radius=[10]
            )
        item.bind(
            size=lambda s, v: setattr(item_bg, 'size', v),
            pos=lambda s, v: setattr(item_bg, 'pos', v)
        )
        
        # Título
        title = Label(
            text=f'{wave_prefix} Batalla #{index} - {played_at}',
            size_hint_y=0.35,
            font_size='13sp',
            bold=True,
            color=COLOR_SECONDARY
        )
        item.add_widget(title)
        
        # Estadísticas
        stats_text = f"Oleadas: {waves} | Duracion: {self._format_duration(duration)}"
        stats = Label(
            text=stats_text,
            size_hint_y=0.35,
            font_size='12sp',
            color=(0.9, 0.9, 0.9, 1)
        )
        item.add_widget(stats)
        
        # Barra de progreso visual
        progress_box = BoxLayout(size_hint_y=0.3, spacing=5)
        wave_percent = min((waves / 20) * 100, 100)  # Asumir 20 oleadas como máximo
        
        bar_bg = Widget(size_hint_x=1)
        with bar_bg.canvas:
            Color(0.2, 0.2, 0.2, 0.5)
            bar_bg_rect = Rectangle(size=bar_bg.size, pos=bar_bg.pos)
        bar_bg.bind(
            size=lambda s, v: setattr(bar_bg_rect, 'size', v),
            pos=lambda s, v: setattr(bar_bg_rect, 'pos', v)
        )
        
        progress_box.add_widget(bar_bg)
        item.add_widget(progress_box)
        
        # Barra de progreso en overlay
        with item.canvas:
            Color(0.2, 0.7, 0.9, 0.7)
            item.progress_rect = Rectangle(
                size=(bar_bg.width * (wave_percent / 100), 15),
                pos=(bar_bg.y, bar_bg.y)
            )
        
        return item
    
    def _format_duration(self, seconds):
        """Convertir segundos a formato MM:SS"""
        minutes = seconds // 60
        secs = seconds % 60
        return f"{int(minutes)}m {int(secs)}s"
    
    def go_back(self, instance):
        """Volver a pantalla de búsqueda"""
        search_screen = self.manager.get_screen('search')
        search_screen.search_input.text = ''
        self.manager.current = 'search'


class BastionDefenderApp(App):
    """App principal"""
    
    def build(self):
        self.title = 'Bastion Defender - Scores'
        
        # Iniciar la API en un hilo separado
        api_thread = threading.Thread(target=run_api, daemon=True)
        api_thread.start()
        print("API iniciada en http://127.0.0.1:8000")
        
        sm = ScreenManager(transition=FadeTransition())
        sm.add_widget(SearchScreen())
        sm.add_widget(ResultsScreen())
        
        return sm


if __name__ == '__main__':
    BastionDefenderApp().run()
