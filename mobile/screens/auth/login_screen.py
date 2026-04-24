# ============================================================
# Écran Connexion Mobile
# Fichier : mobile/screens/auth/login_screen.py
# Description : Écran de connexion avec téléphone + mot de passe
# ============================================================

import asyncio
from kivy.uix.screen import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.clock import Clock
from mobile.theme.colors import Colors
from mobile.services.auth_service import auth_service


class LoginScreen(Screen):
    """Écran de connexion MobiTranz."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "login"
        self._error_label = None
        
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
            hint_text="+241 XX XX XX XX",
            multiline=False,
            input_type="phone",
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
        
        self.error_label = Label(
            text="",
            font_size=14,
            color=Colors.DANGER,
            size_hint_y=None,
            height=30,
            markup=True
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
        layout.add_widget(self.error_label)
        layout.add_widget(login_button)
        layout.add_widget(register_button)
        
        self.add_widget(layout)
    
    def do_login(self, instance):
        phone = self.phone_input.text.strip()
        password = self.password_input.text
        
        if not phone:
            self.error_label.text = "[color=ff4444]Numéro requis[/color=ff4444]"
            return
        if not password:
            self.error_label.text = "[color=ff4444]Mot de passe requis[/color=ff4444]"
            return
        
        self.error_label.text = "[color=44ff44]Connexion en cours...[/color=44ff44]"
        Clock.schedule_once(lambda dt: self._perform_login(phone, password), 0.1)
    
    def _perform_login(self, phone: str, password: str):
        import httpx
        import mobile.config as config
        
        try:
            response = httpx.post(
                f"{config.API_BASE_URL}/auth/login",
                json={"phone": phone, "password": password},
                timeout=config.API_TIMEOUT
            )
            
            if response.status_code == 200:
                data = response.json()
                auth_service.save_tokens(
                    access_token=data.get("access_token", ""),
                    refresh_token=data.get("refresh_token", ""),
                    user_id="current_user",
                    role="client"
                )
                Clock.schedule_once(lambda dt: self._on_login_success(), 0.1)
            elif response.status_code == 401:
                self.error_label.text = "[color=ff4444]Identifiants invalides[/color=ff4444]"
            elif response.status_code == 423:
                self.error_label.text = "[color=ff4444]Compte temporairement verrouillé[/color=ff4444]"
            else:
                self.error_label.text = "[color=ff4444]Erreur serveur[/color=ff4444]"
        
        except httpx.TimeoutException:
            self.error_label.text = "[color=ff4444]Délai dépassé[/color=ff4444]"
        except httpx.ConnectError:
            self.error_label.text = "[color=ff4444]Pas de connexion[/color=ff4444]"
        except Exception as e:
            self.error_label.text = f"[color=ff4444]{str(e)[:50]}[/color=ff4444]"
    
    def _on_login_success(self):
        self.error_label.text = ""
        self.phone_input.text = ""
        self.password_input.text = ""
        self.manager.current = "home"
    
    def go_to_register(self, instance):
        self.manager.current = "register"