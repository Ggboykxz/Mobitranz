# ============================================================
# Point d'entrée Mobile Kivy
# Fichier : mobile/main.py
# Description : Application Kivy principale MobiTranz
# ============================================================

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen, CardTransition

from mobile.screens.auth.login_screen import LoginScreen
from mobile.screens.auth.register_screen import RegisterScreen
from mobile.screens.client.home_screen import HomeScreen


class MobiTranzApp(App):
    """Application mobile MobiTranz.
    
    Point d'entrée de l'application Kivy avec détection
    du rôle utilisateur (client ou taximan).
    """
    
    def build(self):
        """Construit l'interface utilisateur."""
        sm = ScreenManager(transition=CardTransition())
        
        sm.add_widget(LoginScreen())
        sm.add_widget(RegisterScreen())
        sm.add_widget(HomeScreen())
        
        return sm


if __name__ == "__main__":
    MobiTranzApp().run()