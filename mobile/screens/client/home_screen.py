# ============================================================
# Écran Accueil Client
# Fichier : mobile/screens/client/home_screen.py
# Description : Carte avec taxis disponibles et places
# ============================================================

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from mobile.theme.colors import Colors


class HomeScreen(Screen):
    """Écran d'accueil client MobiTranz.
    
    Affiche la carte avec les taxis disponibles.
    """
    
    def __init__(self, **kwargs):
        """Initialise l'écran d'accueil."""
        super().__init__(**kwargs)
        self.name = "home"
        
        layout = BoxLayout(
            orientation="vertical",
            spacing=0
        )
        
        header = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=60,
            padding=20,
            spacing=10
        )
        
        title = Label(
            text="MobiTranz",
            font_size=22,
            color=Colors.PRIMARY,
            size_hint_x=0.7
        )
        
        profile_button = Button(
            text="👤",
            size_hint_x=0.3,
            background_color=Colors.SURFACE,
            on_press=self.go_to_profile
        )
        
        header.add_widget(title)
        header.add_widget(profile_button)
        
        map_area = Label(
            text="[Carte OpenStreetMap]",
            markup=True,
            color=Colors.TEXT_SECONDARY,
            size_hint_y=0.6
        )
        
        action_area = BoxLayout(
            orientation="vertical",
            size_hint_y=0.4,
            padding=20,
            spacing=15
        )
        
        voice_button = Button(
            text="🎤 Proposition vocale",
            background_color=Colors.ACCENT,
            color=(1, 1, 1, 1),
            size_hint_y=None,
            height=60,
            on_press=self.go_to_voice
        )
        
        qr_button = Button(
            text="📷 Scanner QR Code",
            background_color=Colors.PRIMARY,
            color=(1, 1, 1, 1),
            size_hint_y=None,
            height=60,
            on_press=self.go_to_qr_scanner
        )
        
        history_button = Button(
            text="Historique",
            background_color=Colors.SURFACE,
            color=Colors.TEXT_SECONDARY,
            size_hint_y=None,
            height=50,
            on_press=self.go_to_history
        )
        
        action_area.add_widget(voice_button)
        action_area.add_widget(qr_button)
        action_area.add_widget(history_button)
        
        layout.add_widget(header)
        layout.add_widget(map_area)
        layout.add_widget(action_area)
        
        self.add_widget(layout)
    
    def go_to_voice(self, instance):
        """Navigate vers l'écran vocal."""
        self.manager.current = "voice"
    
    def go_to_qr_scanner(self, instance):
        """Navigate vers le scanner QR."""
        self.manager.current = "qr_scanner"
    
    def go_to_history(self, instance):
        """Navigate vers l'historique."""
        self.manager.current = "trip_history"
    
    def go_to_profile(self, instance):
        """Navigate vers le profil."""
        self.manager.current = "profile"