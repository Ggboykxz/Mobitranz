# ============================================================
# Écran de démarrage Vehicle Device
# Fichier : vehicle_device/screens/splash_screen.py
# Description : Écran de chargement/démarrage
# ============================================================

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.properties import ListProperty
from kivy.clock import Clock


class SplashScreen(Screen):
    """Écran de démarrage de l'application véhicule."""
    
    bg_color = ListProperty([0, 0.596, 0.267, 1])
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_once(self.go_to_login, 3)
    
    def on_enter(self):
        """À l'entrée, afficher l'écran de chargement."""
        pass
    
    def go_to_login(self, dt):
        """Naviguer vers l'écran de login."""
        self.manager.current = "login"


class SplashLayout(BoxLayout):
    """Layout principal de l'écran de démarrage."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.padding = 50
        self.spacing = 20
        
        logo = Label(
            text="MobiTranz",
            font_size=72,
            color=[1, 1, 1, 1],
            size_hint_y=None,
            height=150
        )
        
        subtitle = Label(
            text="Système de Transport Gabonais",
            font_size=24,
            color=[0.988, 0.816, 0.086, 1],
            size_hint_y=None,
            height=50
        )
        
        loading = Label(
            text="Chargement...",
            font_size=18,
            color=[0.8, 0.8, 0.8, 1],
            size_hint_y=None,
            height=30
        )
        
        self.add_widget(logo)
        self.add_widget(subtitle)
        self.add_widget(loading)