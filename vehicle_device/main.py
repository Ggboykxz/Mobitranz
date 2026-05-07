# ============================================================
# Point d'entrée Vehicle Device
# Fichier : vehicle_device/main.py
# Description : Interface embarquée véhicule (Raspberry Pi) - KivyMD
# ============================================================

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window

from vehicle_device.screens.splash_screen import SplashScreen
from vehicle_device.screens.login_screen import VehicleLoginScreen
from vehicle_device.screens.idle_screen import IdleScreen
from vehicle_device.screens.proposal_screen import ProposalScreen
from vehicle_device.screens.trip_active_screen import TripActiveScreen
from vehicle_device.screens.trip_completed_screen import TripCompletedScreen


class MobiTranzVehicleApp(App):
    """Application Kivy pour l'unité véhicule Raspberry Pi."""
    
    def build(self):
        """Construction de l'interface."""
        Window.fullscreen = True
        Window.show_cursor = False
        
        sm = ScreenManager()
        
        sm.add_widget(SplashScreen(name="splash"))
        sm.add_widget(VehicleLoginScreen(name="login"))
        sm.add_widget(IdleScreen(name="idle"))
        sm.add_widget(ProposalScreen(name="proposal"))
        sm.add_widget(TripActiveScreen(name="trip_active"))
        sm.add_widget(TripCompletedScreen(name="trip_completed"))
        
        return sm
    
    def on_start(self):
        """Démarrage de l'application."""
        super().on_start()
    
    def on_stop(self):
        """Arrêt de l'application."""
        super().on_stop()


if __name__ == "__main__":
    MobiTranzVehicleApp().run()