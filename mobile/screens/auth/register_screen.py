# ============================================================
# Écran Inscription Mobile
# Fichier : mobile/screens/auth/register_screen.py
# Description : Écran d'inscription client ou taximan
# ============================================================

from kivy.uix.screen import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from mobile.theme.colors import Colors


class RegisterScreen(Screen):
    """Écran d'inscription MobiTranz.
    
    Permet l'inscription d'un nouveau client.
    """
    
    def __init__(self, **kwargs):
        """Initialise l'écran d'inscription."""
        super().__init__(**kwargs)
        self.name = "register"
        
        layout = BoxLayout(
            orientation="vertical",
            padding=50,
            spacing=20
        )
        
        title = Label(
            text="Créer un compte",
            font_size=28,
            color=Colors.PRIMARY,
            size_hint_y=None,
            height=60
        )
        
        self.phone_input = TextInput(
            hint_text="Téléphone (+241 XX XX XX XX)",
            multiline=False,
            input_type="number",
            size_hint_y=None,
            height=50
        )
        
        self.email_input = TextInput(
            hint_text="Email (optionnel)",
            multiline=False,
            input_type="email",
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
        
        self.confirm_password_input = TextInput(
            hint_text="Confirmer mot de passe",
            multiline=False,
            password=True,
            size_hint_y=None,
            height=50
        )
        
        register_button = Button(
            text="S'inscrire",
            background_color=Colors.PRIMARY,
            color=(1, 1, 1, 1),
            size_hint_y=None,
            height=50,
            on_press=self.do_register
        )
        
        back_button = Button(
            text="Retour",
            background_color=Colors.SURFACE,
            color=Colors.TEXT_SECONDARY,
            size_hint_y=None,
            height=50,
            on_press=self.go_back
        )
        
        layout.add_widget(title)
        layout.add_widget(self.phone_input)
        layout.add_widget(self.email_input)
        layout.add_widget(self.password_input)
        layout.add_widget(self.confirm_password_input)
        layout.add_widget(register_button)
        layout.add_widget(back_button)
        
        self.add_widget(layout)
    
    def do_register(self, instance):
        """Traite l'inscription."""
        phone = self.phone_input.text
        password = self.password_input.text
        confirm = self.confirm_password_input.text
        
        if not phone or not password:
            return
        
        if password != confirm:
            return
        
        self.manager.current = "login"
    
    def go_back(self, instance):
        """Retourne à l'écran de connexion."""
        self.manager.current = "login"