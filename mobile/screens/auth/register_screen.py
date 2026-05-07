# ============================================================
# Écran Inscription Mobile
# Fichier : mobile/screens/auth/register_screen.py
# Description : Écran d'inscription client ou taximan
# ============================================================

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.clock import Clock
from mobile.theme.colors import Colors
from mobile.services.auth_service import auth_service


class RegisterScreen(Screen):
    """Écran d'inscription MobiTranz."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "register"
        self._error_label = None
        
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
        
        self.first_name_input = TextInput(
            hint_text="Prénom",
            multiline=False,
            size_hint_y=None,
            height=50
        )
        
        self.last_name_input = TextInput(
            hint_text="Nom",
            multiline=False,
            size_hint_y=None,
            height=50
        )
        
        self.phone_input = TextInput(
            hint_text="+241 XX XX XX XX",
            multiline=False,
            input_type="phone",
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
        
        self.error_label = Label(
            text="",
            font_size=14,
            color=Colors.DANGER,
            size_hint_y=None,
            height=30,
            markup=True
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
        layout.add_widget(self.first_name_input)
        layout.add_widget(self.last_name_input)
        layout.add_widget(self.phone_input)
        layout.add_widget(self.email_input)
        layout.add_widget(self.password_input)
        layout.add_widget(self.confirm_password_input)
        layout.add_widget(self.error_label)
        layout.add_widget(register_button)
        layout.add_widget(back_button)
        
        self.add_widget(layout)
    
    def do_register(self, instance):
        first_name = self.first_name_input.text.strip()
        last_name = self.last_name_input.text.strip()
        phone = self.phone_input.text.strip()
        email = self.email_input.text.strip()
        password = self.password_input.text
        confirm = self.confirm_password_input.text
        
        if not phone:
            self.error_label.text = "[color=ff4444]Numéro requis[/color=ff4444]"
            return
        if not password:
            self.error_label.text = "[color=ff4444]Mot de passe requis[/color=ff4444]"
            return
        if len(password) < 8:
            self.error_label.text = "[color=ff4444]Min. 8 caractères[/color=ff4444]"
            return
        if password != confirm:
            self.error_label.text = "[color=ff4444]Mots de passe différents[/color=ff4444]"
            return
        
        self.error_label.text = "[color=44ff44]Inscription en cours...[/color=44ff44]"
        Clock.schedule_once(
            lambda dt: self._perform_register(phone, password, first_name, last_name, email),
            0.1
        )
    
    def _perform_register(self, phone: str, password: str, first_name: str, last_name: str, email: str):
        import httpx
        import mobile.config as config
        
        payload = {
            "phone": phone,
            "password": password,
            "first_name": first_name or "Client",
            "last_name": last_name or "User",
        }
        if email:
            payload["email"] = email
        
        try:
            response = httpx.post(
                f"{config.API_BASE_URL}/auth/register",
                json=payload,
                timeout=config.API_TIMEOUT
            )
            
            if response.status_code == 201:
                data = response.json()
                auth_service.save_tokens(
                    access_token=data.get("access_token", ""),
                    refresh_token=data.get("refresh_token", ""),
                    user_id="new_user",
                    role="client"
                )
                Clock.schedule_once(lambda dt: self._on_register_success(), 0.1)
            elif response.status_code == 400:
                self.error_label.text = "[color=ff4444]Données invalides[/color=ff4444]"
            elif response.status_code == 409:
                self.error_label.text = "[color=ff4444]Téléphone déjà utilisé[/color=ff4444]"
            else:
                self.error_label.text = "[color=ff4444]Erreur serveur[/color=ff4444]"
        
        except httpx.TimeoutException:
            self.error_label.text = "[color=ff4444]Délai dépassé[/color=ff4444]"
        except httpx.ConnectError:
            self.error_label.text = "[color=ff4444]Pas de connexion[/color=ff4444]"
        except Exception as e:
            self.error_label.text = f"[color=ff4444]{str(e)[:50]}[/color=ff4444]"
    
    def _on_register_success(self):
        self.error_label.text = "[color=44ff44]Compte créé![/color=44ff44]"
        Clock.schedule_once(lambda dt: setattr(self.manager, "current", "home"), 1.5)
    
    def go_back(self, instance):
        self.manager.current = "login"