# ============================================================
# Écran Trajet Actif Client
# Fichier : mobile/screens/client/trip_active_screen.py
# ============================================================

from kivy.uix.screen import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from mobile.theme.colors import Colors


class TripActiveScreen(Screen):
    """Écran de trajet actif pour le client."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "trip_active"
        self._build_ui()
    
    def _build_ui(self):
        layout = BoxLayout(orientation="vertical", padding=20, spacing=16)
        
        # Header
        header = BoxLayout(size_hint_y=None, height=60)
        status_badge = Label(text="🟢 EN COURS", font_size=12, color=Colors.ACCENT, width=120)
        title = Label(text="Trajet en cours", font_size=18, color=Colors.PRIMARY)
        header.add_widget(status_badge)
        header.add_widget(title)
        layout.add_widget(header)
        
        # Map area
        map_area = BoxLayout(size_hint=(1, 0.4), background_color=Colors.GREY_200, radius=[12])
        map_label = Label(text="🗺️\n\nCarte en temps réel", font_size=14, color=Colors.TEXT_SECONDARY)
        map_area.add_widget(map_label)
        layout.add_widget(map_area)
        
        # Trip info
        info = BoxLayout(orientation="vertical", padding=16, background_color=Colors.SURFACE, radius=[12])
        info.add_widget(Label(text="🚗 Conducteur: Jean M.", font_size=14, color=Colors.TEXT_PRIMARY))
        info.add_widget(Label(text="🚕 Véhicule: AA-001-AI (Toyota Prius)", font_size=14, color=Colors.TEXT_SECONDARY))
        info.add_widget(Label(text="⏱️ ETA: 12 minutes", font_size=14, color=Colors.TEXT_SECONDARY))
        info.add_widget(Label(text="📍 Destination: Owendo", font_size=14, color=Colors.TEXT_PRIMARY))
        layout.add_widget(info)
        
        # SOS Button
        sos_btn = Button(text="🚨 SIGNALER UN INCIDENT", height=56, background_color=Colors.DANGER, color=(1,1,1,1))
        sos_btn.bind(on_press=self.report_incident)
        layout.add_widget(sos_btn)
        
        # Complete
        complete_btn = Button(text="✓ Terminer le trajet", height=48, background_color=Colors.ACCENT, color=(1,1,1,1))
        complete_btn.bind(on_press=self.complete_trip)
        layout.add_widget(complete_btn)
        
        self.add_widget(layout)
    
    def report_incident(self, instance):
        """Signale un incident."""
        print("Incident signalé")
    
    def complete_trip(self, instance):
        """Termine le trajet."""
        self.manager.current = "trip_history"