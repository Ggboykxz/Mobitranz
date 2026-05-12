from kivy.clock import Clock
from kivy.uix.screenmanager import Screen
from kivy.properties import ObjectProperty, StringProperty
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton, MDIconButton
from kivymd.uix.spinner import MDSpinner
from kivymd.uix.snackbar import MDSnackbar
from kivymd.uix.topappbar import MDTopAppBar
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.menu import MDDropdownMenu
from kivy.metrics import dp
from mobile.services.api_client import api_client
from mobile.services.cache_service import cache_service


class HomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "home"
        self._menu = None
        self._build_ui()

    def _build_ui(self):
        self.root = MDBoxLayout(orientation="vertical", md_bg_color="#F7F9FC")

        self.top_bar = MDTopAppBar(
            title="MobiTranz",
            md_bg_color="#1A3A6C",
            specific_text_color="#FFFFFF",
            left_action_items=[["menu", lambda x: self.open_menu()]],
            right_action_items=[["account-circle", lambda x: self.go_to_profile()]],
        )
        self.root.add_widget(self.top_bar)

        scroll = MDBoxLayout(orientation="vertical", padding=[20, 10], spacing=16)
        self.greeting_label = MDLabel(
            text="Bonjour !",
            font_style="H5",
            theme_text_color="Primary",
            size_hint_y=None,
            height=dp(40),
        )
        scroll.add_widget(self.greeting_label)

        self.stats_card = MDCard(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(80),
            padding=16,
            spacing=10,
            md_bg_color="#FFFFFF",
            radius=[12],
        )
        self.stats_label = MDLabel(
            text="Chargement des statistiques...",
            theme_text_color="Secondary",
            font_style="Body1",
        )
        self.stats_card.add_widget(self.stats_label)
        scroll.add_widget(self.stats_card)

        menu_grid = MDGridLayout(
            cols=2,
            spacing=16,
            padding=0,
            size_hint_y=None,
            height=dp(320),
        )

        menu_items = [
            ("microphone", "Proposition vocale", "voice"),
            ("qrcode-scan", "Scanner QR", "qr_scanner"),
            ("car", "Trajet actif", "trip_active"),
            ("history", "Historique", "trip_history"),
            ("chat", "Messagerie", "chat"),
            ("bell", "Notifications", "notifications"),
            ("alert", "SOS", "sos_history"),
            ("cog", "Parametres", "settings"),
        ]

        for icon, label_text, screen_name in menu_items:
            card = MDCard(
                orientation="vertical",
                size_hint=(1, None),
                height=dp(70),
                padding=12,
                spacing=4,
                md_bg_color="#FFFFFF",
                radius=[12],
                ripple_behavior=True,
            )
            icon_btn = MDIconButton(
                icon=icon,
                theme_icon_color="Custom",
                icon_color="#1A3A6C",
                pos_hint={"center_x": 0.5},
            )
            label = MDLabel(
                text=label_text,
                font_style="Caption",
                theme_text_color="Secondary",
                halign="center",
                size_hint_y=None,
                height=dp(20),
            )
            card.add_widget(icon_btn)
            card.add_widget(label)
            card.bind(on_release=lambda x, s=screen_name: self.navigate(s))
            menu_grid.add_widget(card)

        scroll.add_widget(menu_grid)

        self.spinner = MDSpinner(
            size_hint=(None, None),
            size=(dp(30), dp(30)),
            pos_hint={"center_x": 0.5},
            active=False,
        )
        scroll.add_widget(self.spinner)

        self.root.add_widget(scroll)
        self.add_widget(self.root)

    def on_enter(self):
        Clock.schedule_once(lambda dt: self.load_data())

    def on_leave(self):
        if hasattr(self, '_dashboard_data'):
            cache_service.set("dashboard", self._dashboard_data)

    def open_menu(self):
        menu_items = [
            {
                "text": "Carte",
                "on_release": lambda x="map": self.navigate("map"),
            },
            {
                "text": "Profil",
                "on_release": lambda x="profile": self.navigate("profile"),
            },
            {
                "text": "Parametres",
                "on_release": lambda x="settings": self.navigate("settings"),
            },
        ]
        self._menu = MDDropdownMenu(
            caller=self.top_bar.ids.get("left_actions", self.top_bar),
            items=menu_items,
            width_mult=4,
        )
        self._menu.open()

    async def load_data(self):
        self.spinner.active = True
        self.hide_offline_banner()
        cached = cache_service.get("dashboard")
        if cached:
            stats = cached.get("stats", {})
            user = cached.get("user", {})
            Clock.schedule_once(lambda dt: self.update_ui(stats, user))
        try:
            data = await api_client.get("/api/v1/dashboard")
            self._dashboard_data = data
            cache_service.set("dashboard", data)
            stats = data.get("stats", {})
            user = data.get("user", {})
            Clock.schedule_once(lambda dt: self.update_ui(stats, user))
            Clock.schedule_once(lambda dt: self.hide_offline_banner())
        except Exception as e:
            if not cached:
                stale = cache_service.get_stale("dashboard")
                if stale:
                    self._dashboard_data = stale
                    s = stale.get("stats", {})
                    u = stale.get("user", {})
                    Clock.schedule_once(lambda dt: self.update_ui(s, u))
                    Clock.schedule_once(lambda dt: self.show_offline_banner())
                else:
                    Clock.schedule_once(lambda dt: self.show_error(str(e)))
        finally:
            Clock.schedule_once(lambda dt: setattr(self.spinner, "active", False))

    def update_ui(self, stats, user):
        self.greeting_label.text = f"Bonjour {user.get('first_name', 'cher client')} !"
        trips_count = stats.get("trips_count", 0)
        total_spent = stats.get("total_spent", 0)
        rating = stats.get("rating", 0)
        self.stats_label.text = (
            f"Trajets: {trips_count}  |  Depense: {total_spent} XAF  |  Note: {rating}/5"
        )

    def show_error(self, message):
        self.stats_label.text = "Erreur de chargement"
        MDSnackbar(text=f"Erreur: {message}", snackbar_x=10, snackbar_y=10).open()

    def navigate(self, screen_name):
        if self.manager and hasattr(self.manager, "current"):
            self.manager.switch(screen_name)

    def go_to_profile(self):
        self.manager.switch("profile")

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
