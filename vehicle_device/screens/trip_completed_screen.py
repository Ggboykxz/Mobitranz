# ============================================================
# Écran trajet terminé Vehicle Device
# Fichier : vehicle_device/screens/trip_completed_screen.py
# Description : Écran de confirmation de fin de trajet
# ============================================================

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.properties import StringProperty
import structlog


logger = structlog.get_logger()


class TripCompletedScreen(Screen):
    """Écran affiché à la fin d'un trajet."""
    
    amount = StringProperty("0")
    rating = StringProperty("5.0")
    
    def on_enter(self):
        """À l'entrée, afficher le résumé."""
        pass
    
    def go_to_idle(self):
        """Retour à l'écran d'attente."""
        self.manager.current = "idle"


class TripCompletedLayout(BoxLayout):
    """Layout de l'écran trajet terminé."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.padding = 40
        self.spacing = 25
        
        success = Label(
            text="TRAJET TERMINÉ",
            font_size=36,
            color=[0, 0.8, 0.4, 1],
            size_hint_y=None,
            height=80
        )
        
        amount_label = Label(
            text="Montant collectées:",
            font_size=24,
            color=[0.9, 0.9, 0.9, 1]
        )
        
        self.amount_label = Label(
            text="0 XAF",
            font_size=48,
            color=[0.988, 0.816, 0.086, 1]
        )
        
        info = Label(
            text="Merci de votre confiance!",
            font_size=18,
            color=[0.7, 0.7, 0.7, 1]
        )
        
        continue_btn = Button(
            text="Prêt pour le prochain client",
            font_size=22,
            size_hint_y=None,
            height=70,
            background_color=[0, 0.596, 0.267, 1]
        )
        
        self.add_widget(success)
        self.add_widget(amount_label)
        self.add_widget(self.amount_label)
        self.add_widget(info)
        self.add_widget(continue_btn)