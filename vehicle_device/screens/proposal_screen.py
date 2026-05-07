# ============================================================
# Écran de proposition de trajet Vehicle Device
# Fichier : vehicle_device/screens/proposal_screen.py
# Description : Affichage d'une proposition de trajet avec lecture TTS
# ============================================================

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.properties import ListProperty, StringProperty
from kivy.clock import Clock
import structlog

from vehicle_device.hardware.klaxon_detector import klaxon_detector


logger = structlog.get_logger()


class ProposalScreen(Screen):
    """Écran d'affichage d'une proposition de trajet."""
    
    bg_color = ListProperty([0.012, 0.247, 0.176, 1])
    client_name = StringProperty("Client")
    pickup = StringProperty("Départ")
    destination = StringProperty("Destination")
    amount = StringProperty("0")
    
    def on_enter(self):
        """À l'entrée, lire la proposition et écouter le klaxon."""
        self.start_tts()
        self.start_klaxon_listening()
    
    def on_leave(self):
        """À la sortie, arrêter l'écoute du klaxon."""
        klaxon_detector.stop_listening()
    
    def start_tts(self):
        """Démarre la lecture vocale de la proposition."""
        message = f"Nouveau client: {self.client_name}. Trajet de {self.pickup} vers {self.destination}. Montant: {self.amount} francs."
        
        try:
            import pyttsx3
            engine = pyttsx3.init()
            engine.say(message)
            engine.runAndWait()
        except Exception as e:
            logger.warning("TTS échoué", error=str(e))
    
    def start_klaxon_listening(self):
        """Démarre l'écoute du klaxon."""
        def on_klaxon_result(result):
            if result == 1:
                logger.info("Klaxon acceptation détecté")
                self.accept_trip()
            elif result == 2:
                logger.info("Klaxon refus détecté")
                self.refuse_trip()
        
        klaxon_detector.start_listening(on_klaxon_result)
        
        Clock.schedule_once(self.check_timeout, 10)
    
    def check_timeout(self, dt):
        """Vérifie le timeout."""
        if not klaxon_detector.beeps_detected:
            logger.info("Timeout - refus automatique")
            self.refuse_trip()
    
    def accept_trip(self):
        """Accepte le trajet."""
        klaxon_detector.stop_listening()
        self.manager.current = "trip_active"
    
    def refuse_trip(self):
        """Refuse le trajet."""
        klaxon_detector.stop_listening()
        self.manager.current = "idle"


class ProposalLayout(BoxLayout):
    """Layout de l'écran de proposition."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.padding = 30
        self.spacing = 20
        
        title = Label(
            text="NOUVELLE PROPOSITION",
            font_size=28,
            color=[0.988, 0.816, 0.086, 1],
            size_hint_y=None,
            height=60
        )
        
        self.client_label = Label(
            text="Client:",
            font_size=24,
            color=[1, 1, 1, 1]
        )
        
        self.route_label = Label(
            text="Route:",
            font_size=20,
            color=[0.9, 0.9, 0.9, 1]
        )
        
        self.amount_label = Label(
            text="Montant:",
            font_size=32,
            color=[0, 0.8, 0.4, 1]
        )
        
        instruction = Label(
            text="Klaxonnez 1 fois pour ACCEPTÉ\nKlaxonnez 2 fois pour REFUSÉ",
            font_size=16,
            color=[0.7, 0.7, 0.7, 1],
            halign="center"
        )
        
        self.add_widget(title)
        self.add_widget(self.client_label)
        self.add_widget(self.route_label)
        self.add_widget(self.amount_label)
        self.add_widget(instruction)