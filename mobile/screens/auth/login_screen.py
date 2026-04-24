# ============================================================
# Écran Connexion Mobile
# Fichier : mobile/screens/auth/login_screen.py
# Description : Écran de connexion avec téléphone + mot de passe
# ============================================================

from kivy.uix.screen import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from mobile.theme.colors import Colors


class LoginScreen(Screen):
    """Écran de connexion MobiTranz.
    
    Permet la connexion avec téléphone et mot de passe.
    """
    
    def __init__(self, **kwargs):
        """Initialise l'écran de connexion."""
        super().__init__(**kwargs)
        self.name = "login"
        
        layout = BoxLayout(
            orientation="vertical",
            padding=50,
            spacing=20
        )
        
        title = Label(
            text="MobiTranz",
            font_size=32,
            color=Colors.PRIMARY,
            size_hint_y=None,
            height=60
        )
        
        subtitle = Label(
            text="Connexion",
            font_size=18,
            color=Colors.TEXT_SECONDARY
        )
        
        self.phone_input = TextInput(
            hint_text="Téléphone (+241 XX XX XX XX)",
            multiline=False,
            input_type="number",
            size_hint_y=None,
            height=50
        )
        
        self.password_input = TextInput(
            hint_text="Mot de passe",
            multiline=False,
            password=True,
            size_hint_y=None,
            height=50
        )
        
        login_button = Button(
            text="Se connecter",
            background_color=Colors.PRIMARY,
            color=(1, 1, 1, 1),
            size_hint_y=None,
            height=50,
            on_press=self.do_login
        )
        
        register_button = Button(
            text="S'inscrire",
            background_color=Colors.SURFACE,
            color=Colors.PRIMARY,
            size_hint_y=None,
            height=50,
            on_press=self.go_to_register
        )
        
        layout.add_widget(title)
        layout.add_widget(subtitle)
        layout.add_widget(self.phone_input)
        layout.add_widget(self.password_input)
        layout.add_widget(login_button)
        layout.add_widget(register_button)
        
        self.add_widget(layout)
    
    def do_login(self, instance):
        """Traite la connexion."""
        phone = self.phone_input.text
        password = self.password_input.text
        
        if not phone or not password:
            return
        
        self.manager.current = "home"
    
    def go_to_register(self, instance):
        """Navigate vers l'écran d'inscription."""
        self.manager.current = "register"