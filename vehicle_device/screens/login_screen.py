# ============================================================
# Écran de connexion Vehicle Device
# Fichier : vehicle_device/screens/login_screen.py
# Description : Authentification conducteur sur le Raspberry Pi
# ============================================================

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.spinner import Spinner
from kivy.properties import ListProperty
import structlog

from kivy.core.window import Window


logger = structlog.get_logger()


class VehicleLoginScreen(Screen):
    """Écran de connexion pour le conducteur."""
    
    bg_color = ListProperty([0.012, 0.247, 0.176, 1])
    
    def on_enter(self):
        """À l'entrée, afficher le formulaire."""
        pass
    
    def authenticate(self, pin: str, fingerprint: bool = False):
        """Authentifie le conducteur.
        
        Args:
            pin: PIN à 6 chiffres
            fingerprint: True si authentification par empreinte
        """
        logger.info("Tentative authentification", fingerprint=fingerprint)
        
        if len(pin) == 6 or fingerprint:
            self.manager.current = "idle"
        else:
            logger.warning("PIN invalide", pin_length=len(pin))


class LoginLayout(BoxLayout):
    """Layout du formulaire de connexion."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.padding = 50
        self.spacing = 30
        
        title = Label(
            text="MobiTranz Conducteur",
            font_size=36,
            color=[1, 1, 1, 1],
            size_hint_y=None,
            height=80
        )
        
        pin_label = Label(
            text="Entrez votre PIN",
            font_size=20,
            color=[0.8, 0.8, 0.8, 1],
            size_hint_y=None,
            height=40
        )
        
        self.pin_input = TextInput(
            password=True,
            password_mask="*",
            multiline=False,
            font_size=32,
            halign="center",
            size_hint_y=None,
            height=80
        )
        
        self.fingerprint_btn = Button(
            text="S'authentifier par empreinte",
            font_size=18,
            size_hint_y=None,
            height=60,
            background_color=[0.2, 0.2, 0.2, 1]
        )
        
        login_btn = Button(
            text="Se connecter",
            font_size=20,
            size_hint_y=None,
            height=60,
            background_color=[0, 0.596, 0.267, 1]
        )
        
        self.add_widget(title)
        self.add_widget(pin_input)
        self.add_widget(self.pin_input)
        self.add_widget(self.fingerprint_btn)
        self.add_widget(login_btn)