from kivy.clock import Clock
from kivy.uix.screenmanager import Screen
from kivy.storage.jsonstore import JsonStore
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton, MDFlatButton, MDIconButton
from kivymd.uix.spinner import MDSpinner
from kivymd.uix.snackbar import MDSnackbar
from kivymd.uix.topappbar import MDTopAppBar
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.switch import MDSwitch
from kivymd.uix.dialog import MDDialog
from kivy.metrics import dp
from mobile.theme.theme import MobiTranzTheme
from mobile.ui.haptic import Haptic


class SettingsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "settings"
        self._store = JsonStore("mobitranz_settings.json")
        self._defaults = {
            "push_notifications": True,
            "sms_notifications": True,
            "sounds": True,
            "location_sharing": True,
            "trip_history": True,
            "language": "Francais",
            "currency": "XAF",
            "dark_mode": False,
        }
        self._dialog = None
        self._build_ui()

    def _build_ui(self):
        stored_dark = self._load_setting("dark_mode")
        bg = "#1E1E2E" if stored_dark else "#F7F9FC"
        card_bg = "#2D2D44" if stored_dark else "#FFFFFF"
        text_color = "#FFFFFF" if stored_dark else "#1A3A6C"

        self.root = MDBoxLayout(orientation="vertical", md_bg_color=bg)

        self.top_bar = MDTopAppBar(
            title="Parametres",
            md_bg_color="#1A3A6C",
            specific_text_color="#FFFFFF",
            left_action_items=[["arrow-left", lambda x: self.go_back()]],
        )
        self.root.add_widget(self.top_bar)

        scroll = MDScrollView(size_hint=(1, 1))
        content = MDBoxLayout(
            orientation="vertical",
            padding=[16, 8],
            spacing=4,
            size_hint_y=None,
        )
        content.bind(minimum_height=content.setter("height"))

        sections = [
            ("Compte", [
                ("account-edit", "Modifier le profil", self.edit_profile),
                ("lock", "Changer mot de passe", self.change_password),
                ("credit-card", "Moyens de paiement", self.manage_payment),
            ]),
            ("Notifications", [
                ("bell", "Notifications push", "push_notifications"),
                ("message-text", "Notifications SMS", "sms_notifications"),
                ("volume-high", "Sons", "sounds"),
            ]),
            ("Confidentialite", [
                ("map-marker", "Partage de position", "location_sharing"),
                ("history", "Historique trajets", "trip_history"),
            ]),
            ("Application", [
                ("translate", "Langue", self.change_language),
                ("currency-usd", "Devise", self.change_currency),
                ("help-circle", "Aide et support", self.open_help),
                ("bug", "Signaler un probleme", self.report_issue),
            ]),
            ("Theme", [
                ("theme-light-dark", "Mode sombre", "dark_mode"),
            ]),
            ("A propos", [
                ("information", "Version 1.0.0", self.show_about),
                ("file-document", "Conditions utilisation", self.show_terms),
                ("shield-account", "Politique confidentialite", self.show_privacy),
            ]),
        ]

        for section_title, items in sections:
            content.add_widget(self._create_section_header(section_title, stored_dark))
            for item in items:
                if len(item) == 3 and item[1] in self._defaults:
                    content.add_widget(self._create_toggle_row(item[0], item[1], item[2], stored_dark, card_bg))
                else:
                    content.add_widget(self._create_action_row(item[0], item[1], item[2], stored_dark, card_bg))

        content.add_widget(MDBoxLayout(size_hint_y=None, height=dp(16)))

        logout_btn = MDRaisedButton(
            text="Deconnexion",
            md_bg_color="#E53E3E",
            text_color="#FFFFFF",
            size_hint=(1, None),
            height=dp(50),
            on_release=self.logout,
        )
        content.add_widget(logout_btn)

        scroll.add_widget(content)
        self.root.add_widget(scroll)
        self.add_widget(self.root)

    def _create_section_header(self, title, is_dark=False):
        header = MDBoxLayout(
            orientation="vertical",
            size_hint_y=None,
            height=dp(36),
            padding=[4, 8, 4, 0],
        )
        header.add_widget(MDLabel(
            text=title.upper(),
            font_style="Caption",
            theme_text_color="Custom",
            text_color="#009E60",
            bold=True,
        ))
        return header

    def _create_action_row(self, icon, text, callback, is_dark=False, card_bg="#FFFFFF"):
        row = MDCard(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(52),
            padding=[12, 8],
            spacing=12,
            md_bg_color=card_bg,
            radius=[8],
            ripple_behavior=True,
        )
        ico = MDIconButton(icon=icon, icon_color="#1A3A6C", theme_icon_size="Custom", icon_size=dp(22))
        lbl = MDLabel(text=text, font_style="Body1", theme_text_color="Primary")
        arrow = MDIconButton(
            icon="chevron-right",
            icon_color="#A0AEC0",
            theme_icon_size="Custom",
            icon_size=dp(20),
            size_hint_x=None,
            width=dp(30),
        )
        row.add_widget(ico)
        row.add_widget(lbl)
        row.add_widget(arrow)
        row.bind(on_release=lambda x, cb=callback: cb())
        return row

    def _create_toggle_row(self, icon, text, key, is_dark=False, card_bg="#FFFFFF"):
        row = MDCard(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(52),
            padding=[12, 8],
            spacing=12,
            md_bg_color=card_bg,
            radius=[8],
        )
        ico = MDIconButton(icon=icon, icon_color="#1A3A6C", theme_icon_size="Custom", icon_size=dp(22))
        lbl = MDLabel(text=text, font_style="Body1", theme_text_color="Primary")

        switch = MDSwitch(
            active=self._load_setting(key),
            size_hint_x=None,
            width=dp(50),
        )
        if key == "dark_mode":
            switch.bind(active=self._on_dark_mode_toggle)
        else:
            switch.bind(active=lambda s, val, k=key: self._save_setting(k, val))

        row.add_widget(ico)
        row.add_widget(lbl)
        row.add_widget(switch)
        return row

    def _load_setting(self, key):
        try:
            return self._store.get(key)["value"]
        except KeyError:
            return self._defaults.get(key, False)

    def _save_setting(self, key, value):
        self._store.put(key, value=value)
        MDSnackbar(
            text=f"{key.replace('_', ' ').title()}: {'Active' if value else 'Desactive'}",
            snackbar_x=10,
            snackbar_y=10,
            duration=1.5,
        ).open()

    def _on_dark_mode_toggle(self, instance, value):
        self._save_setting("dark_mode", value)
        MobiTranzTheme.set_dark_mode(value)
        Clock.schedule_once(lambda dt: self._rebuild_ui())

    def _rebuild_ui(self):
        self.root.clear_widgets()
        self._build_ui()

    def go_back(self):
        self.manager.switch("home")

    def edit_profile(self):
        self.manager.switch("profile")

    def change_password(self):
        self._show_dialog("Changer mot de passe", "Fonctionnalite a venir")

    def manage_payment(self):
        self.manager.switch("payment")

    def change_language(self):
        self._show_dialog("Langue", "Francais\nEnglish")

    def change_currency(self):
        self._show_dialog("Devise", "XAF (FCFA)\nEUR\nUSD")

    def open_help(self):
        self._show_dialog("Aide", "Contactez le support au +241 XX XX XX XX\nou par email: support@mobitranz.com")

    def report_issue(self):
        self._show_dialog("Signaler", "Envoyez un email a bug@mobitranz.com")

    def show_about(self):
        self._show_dialog("MobiTranz", "Version 1.0.0\n(c) 2026 MobiTranz")

    def show_terms(self):
        self._show_dialog("Conditions", "Consultez les conditions sur mobitranz.com/terms")

    def show_privacy(self):
        self._show_dialog("Confidentialite", "Consultez la politique sur mobitranz.com/privacy")

    def _show_dialog(self, title, text):
        if not self._dialog:
            self._dialog = MDDialog(
                title=title,
                text=text,
                buttons=[
                    MDFlatButton(text="FERMER", on_release=lambda x: self._dialog.dismiss()),
                ],
            )
        else:
            self._dialog.title = title
            self._dialog.text = text
        self._dialog.open()

    def logout(self):
        from mobile.services.api_client import api_client
        api_client._access_token = None
        self.manager.switch("login")
