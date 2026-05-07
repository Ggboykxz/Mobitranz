# ============================================================
# Écran trajet en cours Vehicle Device
# Fichier : vehicle_device/screens/trip_active_screen.py
# Description : Affichage du trajet en cours avec navigation
# ============================================================

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.properties import StringProperty
import structlog


logger = structlog.get_logger()


class TripActiveScreen(Screen):
    """Écran d'affichage du trajet en cours."""
    
    destination = StringProperty("Destination")
    eta = StringProperty("0 min")
    distance = StringProperty("0 km")
    
    def on_enter(self):
        """À l'entrée, démarrer le suivi GPS."""
        self.start_gps_tracking()
    
    def on_leave(self):
        """À la sortie, arrêter le suivi GPS."""
        pass
    
    def start_gps_tracking(self):
        """Démarre le suivi GPS."""
        try:
            from vehicle_device.hardware.gps import gps_service
            
            def on_location(lat, lon, speed):
                self.update_location(lat, lon, speed)
            
            gps_service.start_tracking(on_location)
        except Exception as e:
            logger.warning("GPS non disponible", error=str(e))
    
    def update_location(self, lat, lon, speed):
        """Met à jour la position."""
        pass
    
    def end_trip(self):
        """Termine le trajet."""
        self.manager.current = "trip_completed"


class TripActiveLayout(BoxLayout):
    """Layout de l'écran trajet en cours."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.padding = 30
        self.spacing = 20
        
        status = Label(
            text="TRAJET EN COURS",
            font_size=28,
            color=[0, 0.8, 0.4, 1],
            size_hint_y=None,
            height=60
        )
        
        dest_label = Label(
            text="Vers:",
            font_size=24,
            color=[1, 1, 1, 1]
        )
        
        self.destination_label = Label(
            text="Destination",
            font_size=20,
            color=[0.9, 0.9, 0.9, 1]
        )
        
        info = Label(
            text="GPS: Actif | Caméra: Enregistrement",
            font_size=16,
            color=[0.7, 0.7, 0.7, 1]
        )
        
        complete_btn = Button(
            text="Arrivée - Terminer le trajet",
            font_size=20,
            size_hint_y=None,
            height=60,
            background_color=[0.988, 0.816, 0.086, 1]
        )
        
        self.add_widget(status)
        self.add_widget(dest_label)
        self.add_widget(self.destination_label)
        self.add_widget(info)
        self.add_widget(complete_btn)