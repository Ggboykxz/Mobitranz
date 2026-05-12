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


class RegisterScreen(BaseScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "register"

        layout = MDBoxLayout(
            orientation="vertical",
            padding=[50, 40, 50, 50],
            spacing=14,
            adaptive_height=False,
        )

        title = MDLabel(
            text="Créer un compte",
            font_size=28,
            halign="center",
            theme_text_color="Custom",
            text_color=MobiTranzTheme.PRIMARY,
            size_hint_y=None,
            height=60,
            bold=True,
        )

        self.first_name_input = MDTextField(
            hint_text="Prénom",
            mode="rectangle",
            size_hint_y=None,
            height=50,
        )

        self.last_name_input = MDTextField(
            hint_text="Nom",
            mode="rectangle",
            size_hint_y=None,
            height=50,
        )

        self.phone_input = MDTextField(
            hint_text="+241 XX XX XX XX",
            mode="rectangle",
            size_hint_y=None,
            height=50,
        )

        self.email_input = MDTextField(
            hint_text="Email (optionnel)",
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

        self.confirm_password_input = MDTextField(
            hint_text="Confirmer mot de passe",
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

        register_button = MDRaisedButton(
            text="S'inscrire",
            size_hint=(1, None),
            height=50,
            md_bg_color=MobiTranzTheme.PRIMARY,
            on_release=self.do_register,
        )

        back_btn = MDTextButton(
            text="Déjà un compte ? Connectez-vous",
            on_release=self.go_back,
            pos_hint={"center_x": 0.5},
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
        layout.add_widget(back_btn)

        self.add_widget(layout)

    def do_register(self, instance):
        first_name = self.first_name_input.text.strip()
        last_name = self.last_name_input.text.strip()
        phone = self.phone_input.text.strip()
        email = self.email_input.text.strip()
        password = self.password_input.text
        confirm = self.confirm_password_input.text

        if not phone:
            self.error_label.text = "Numéro requis"
            return
        if not password:
            self.error_label.text = "Mot de passe requis"
            return
        if len(password) < 8:
            self.error_label.text = "Min. 8 caractères"
            return
        if password != confirm:
            self.error_label.text = "Mots de passe différents"
            return

        self.error_label.text = ""
        self.show_loading()

        async def _register():
            payload = {
                "phone": phone,
                "password": password,
                "first_name": first_name or "Client",
                "last_name": last_name or "User",
            }
            if email:
                payload["email"] = email
            return await api_client.register(**payload)

        def handle_result(result):
            self.hide_loading()
            auth_service.save_tokens(
                access_token=result.get("access_token", ""),
                refresh_token=result.get("refresh_token", ""),
                user_id=result.get("user_id", ""),
                role=result.get("role", "client"),
            )
            api_client.set_token(result.get("access_token", ""))
            self.show_toast("Compte créé avec succès!")
            Clock.schedule_once(lambda dt: setattr(self.manager, "current", "home"), 1.0)

        def handle_error(error):
            self.hide_loading()
            status_code = getattr(error, "response", None)
            if status_code is not None:
                sc = getattr(status_code, "status_code", None)
                if sc == 400:
                    self.error_label.text = "Données invalides"
                elif sc == 409:
                    self.error_label.text = "Téléphone déjà utilisé"
                else:
                    self.error_label.text = "Erreur serveur"
            elif "Timeout" in type(error).__name__:
                self.error_label.text = "Délai dépassé"
            elif "Connect" in type(error).__name__:
                self.error_label.text = "Pas de connexion"
            else:
                self.error_label.text = str(error)[:60]

        def run():
            try:
                result = asyncio.run(_register())
                Clock.schedule_once(lambda dt: handle_result(result), 0)
            except Exception as e:
                Clock.schedule_once(lambda dt: handle_error(e), 0)

        import threading
        threading.Thread(target=run, daemon=True).start()

    def go_back(self, instance):
        self.manager.current = "login"
