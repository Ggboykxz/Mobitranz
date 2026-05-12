from kivy.clock import Clock
from kivy.metrics import dp
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.label import MDLabel
from kivymd.uix.spinner import MDSpinner
from kivymd.uix.snackbar import MDSnackbar, MDSnackbarText
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivy.core.window import Window
from mobile.services.cache_service import cache_service


class BaseScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._loading_layout = None
        self._snackbar = None
        self._header = None

    def build_header(self, title="", show_back=True):
        if self._header:
            return self._header
        self._header = MDTopAppBar(
            title=title,
            anchor_title="left",
            md_bg_color=self.theme_cls.primary_color if hasattr(self, "theme_cls") else None,
            specific_text_color="#FFFFFF",
            left_action_items=[["arrow-left", lambda x: self.on_back_button()]] if show_back else [],
        )
        self.add_widget(self._header)
        return self._header

    def show_loading(self):
        if self._loading_layout:
            return
        self._loading_layout = MDBoxLayout(
            md_bg_color=[0, 0, 0, 0.4],
            size_hint=(1, 1),
            pos_hint={"x": 0, "y": 0},
        )
        spinner_box = MDBoxLayout(
            orientation="vertical",
            size_hint=(None, None),
            size=(dp(120), dp(120)),
            pos_hint={"center_x": 0.5, "center_y": 0.5},
            md_bg_color=[1, 1, 1, 0.9],
            radius=[dp(12)],
            spacing=dp(12),
            padding=dp(20),
        )
        spinner = MDSpinner(
            size_hint=(None, None),
            size=(dp(46), dp(46)),
            pos_hint={"center_x": 0.5},
            active=True,
        )
        spinner_box.add_widget(spinner)
        lbl = MDLabel(
            text="Chargement...",
            halign="center",
            font_size=14,
            theme_text_color="Secondary",
        )
        spinner_box.add_widget(lbl)
        self._loading_layout.add_widget(spinner_box)
        self.add_widget(self._loading_layout)
        self._loading_layout.z = 999

    def hide_loading(self):
        if self._loading_layout:
            if self._loading_layout.parent:
                self.remove_widget(self._loading_layout)
            self._loading_layout = None

    def show_toast(self, text, duration=2.0):
        try:
            self._snackbar = MDSnackbar(
                MDSnackbarText(text=text),
                y=dp(56),
                pos_hint={"center_x": 0.5},
                size_hint_x=0.9,
                duration=duration,
            )
            self._snackbar.open()
        except Exception:
            pass

    def show_error(self, text):
        self.show_toast(text, duration=4.0)

    def show_confirm(self, text, callback):
        dialog = MDDialog(
            text=text,
            buttons=[
                MDFlatButton(
                    text="Annuler",
                    on_release=lambda x: dialog.dismiss(),
                ),
                MDFlatButton(
                    text="Confirmer",
                    on_release=lambda x: (callback(), dialog.dismiss()),
                ),
            ],
        )
        dialog.open()

    def safe_ui_update(self, callback):
        Clock.schedule_once(lambda dt: callback())

    def show_offline_banner(self):
        if hasattr(self, '_offline_banner') and self._offline_banner:
            return
        self._offline_banner = MDLabel(
            text="⚠ Mode hors-ligne - Données en cache",
            size_hint_y=None,
            height=dp(30),
            md_bg_color="#FCD116",
            theme_text_color="Custom",
            text_color="#1A202C",
            halign="center",
            font_size=12,
        )
        self.add_widget(self._offline_banner)

    def hide_offline_banner(self):
        if hasattr(self, '_offline_banner') and self._offline_banner:
            if self._offline_banner.parent:
                self.remove_widget(self._offline_banner)
            self._offline_banner = None

    def on_back_button(self):
        if self.manager and len(self.manager.screen_names) > 0:
            self.manager.current = self.manager.screen_names[
                max(0, self.manager.screen_names.index(self.name) - 1)
            ]
