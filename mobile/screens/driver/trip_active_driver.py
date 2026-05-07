# ============================================================
# Écran Trajet Actif Taximan
# Fichier : mobile/screens/driver/trip_active_driver.py
# ============================================================

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from mobile.theme.colors import Colors


class TripActiveDriverScreen(Screen):
    """Écran de trajet actif pour le taximan."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "trip_active_driver"
        self._build_ui()
    
    def _build_ui(self):
        layout = BoxLayout(orientation="vertical", padding=20, spacing=16)
        
        # Status
        status = Label(text="🟢 TRAJET EN COURS", font_size=16, color=Colors.ACCENT)
        layout.add_widget(status)
        
        # Map
        map_area = BoxLayout(size_hint=(1, 0.35), background_color=Colors.GREY_200, radius=[12])
        map_area.add_widget(Label(text="🗺️ GPS", font_size=14))
        layout.add_widget(map_area)
        
        # Client info
        client = BoxLayout(orientation="vertical", padding=16, background_color=Colors.SURFACE, radius=[12])
        client.add_widget(Label(text="Client: Marie", font_size=16, color=Colors.PRIMARY))
        client.add_widget(Label(text="→ Centre-ville", font_size=14, color=Colors.TEXT_PRIMARY))
        client.add_widget(Label(text="1,500 XAF · 2 places", font_size=14, color=Colors.TEXT_SECONDARY))
        layout.add_widget(client)
        
        # Camera toggle
        self.camera_btn = Button(text="📹 Caméra: OFF", height=48, background_color=Colors.GREY_400, color=(1,1,1,1))
        self.camera_btn.bind(on_press=self.toggle_camera)
        layout.add_widget(self.camera_btn)
        
        # Actions
        actions = BoxLayout(size_hint_y=None, height=60, spacing=12)
        
        sos_btn = Button(text="🚨 SOS", background_color=Colors.DANGER, color=(1,1,1,1))
        complete_btn = Button(text="✓ Terminer", background_color=Colors.ACCENT, color=(1,1,1,1), on_press=self.complete)
        
        actions.add_widget(sos_btn)
        actions.add_widget(complete_btn)
        layout.add_widget(actions)
        
        self.add_widget(layout)
    
    def toggle_camera(self, instance):
        """Active/désactive la caméra."""
        if "OFF" in instance.text:
            instance.text = "📹 Caméra: ON"
            instance.background_color = Colors.DANGER
        else:
            instance.text = "📹 Caméra: OFF"
            instance.background_color = Colors.GREY_400
    
    def complete(self, instance):
        """Termine le trajet."""
        self.manager.current = "driver_home"