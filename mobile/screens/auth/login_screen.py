import asyncio
from kivy.clock import Clock
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRaisedButton, MDTextButton
from kivymd.uix.label import MDLabel
from mobile.screens.base_screen import BaseScreen
from mobile.services.api_client import api_client
from mobile.services.auth_service import auth_service
from mobile.theme.theme import MobiTranzTheme


class LoginScreen(BaseScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "login"

        layout = MDBoxLayout(
            orientation="vertical",
            padding=[50, 80, 50, 50],
            spacing=20,
        )

        title = MDLabel(
            text="MobiTranz",
            font_size=32,
            halign="center",
            theme_text_color="Custom",
            text_color=MobiTranzTheme.PRIMARY,
            size_hint_y=None,
            height=60,
            bold=True,
        )

        subtitle = MDLabel(
            text="Connexion",
            font_size=18,
            halign="center",
            theme_text_color="Secondary",
            size_hint_y=None,
            height=30,
        )

        self.phone_input = MDTextField(
            hint_text="+241 XX XX XX XX",
            mode="rectangle",
            size_hint_y=None,
            height=50,
        )

        self.password_input = MDTextField(
            hint_text="Mot de passe",
            mode="rectangle",
            password=True,
            size_hint_y=None,
            height=50,
        )

        self.error_label = MDLabel(
            text="",
            font_size=14,
            halign="center",
            theme_text_color="Error",
            size_hint_y=None,
            height=30,
        )

        login_button = MDRaisedButton(
            text="Se connecter",
            size_hint=(1, None),
            height=50,
            md_bg_color=MobiTranzTheme.PRIMARY,
            on_release=self.do_login,
        )

        register_btn = MDTextButton(
            text="Créer un compte",
            on_release=self.go_to_register,
            pos_hint={"center_x": 0.5},
        )

        layout.add_widget(title)
        layout.add_widget(subtitle)
        layout.add_widget(self.phone_input)
        layout.add_widget(self.password_input)
        layout.add_widget(self.error_label)
        layout.add_widget(login_button)
        layout.add_widget(register_btn)

        self.add_widget(layout)

    def do_login(self, instance):
        phone = self.phone_input.text.strip()
        password = self.password_input.text

        if not phone:
            self.error_label.text = "Numéro requis"
            return
        if not password:
            self.error_label.text = "Mot de passe requis"
            return

        self.error_label.text = ""
        self.show_loading()

        async def _login():
            result = await api_client.login(phone, password)
            return result

        def handle_result(result):
            self.hide_loading()
            auth_service.save_tokens(
                access_token=result.get("access_token", ""),
                refresh_token=result.get("refresh_token", ""),
                user_id=result.get("user_id", ""),
                role=result.get("role", "client"),
            )
            api_client.set_token(result.get("access_token", ""))
            self.phone_input.text = ""
            self.password_input.text = ""
            self.manager.switch("home")

        def handle_error(error):
            self.hide_loading()
            status_code = getattr(error, "response", None)
            if status_code is not None:
                sc = getattr(status_code, "status_code", None)
                if sc == 401:
                    self.error_label.text = "Identifiants invalides"
                elif sc == 423:
                    self.error_label.text = "Compte temporairement verrouillé"
                else:
                    self.error_label.text = "Erreur serveur"
            elif hasattr(error, "__class__") and "Timeout" in error.__class__.__name__:
                self.error_label.text = "Délai dépassé"
            elif "Connect" in str(type(error).__name__):
                self.error_label.text = "Pas de connexion"
            else:
                self.error_label.text = str(error)[:60]

        def run():
            try:
                result = asyncio.run(_login())
                Clock.schedule_once(lambda dt: handle_result(result), 0)
            except Exception as e:
                Clock.schedule_once(lambda dt: handle_error(e), 0)

        import threading
        threading.Thread(target=run, daemon=True).start()

    def go_to_register(self, instance):
        self.manager.switch("register")
