from kivy.clock import Clock
from kivy.uix.screenmanager import Screen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton, MDFlatButton, MDIconButton
from kivymd.uix.spinner import MDSpinner
from kivymd.uix.snackbar import MDSnackbar
from kivymd.uix.topappbar import MDTopAppBar
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.list import TwoLineListItem, ThreeLineListItem
from kivy.metrics import dp
from mobile.services.api_client import api_client
from mobile.services.cache_service import cache_service
from mobile.ui.shimmer_list import ShimmerTripCard, ShimmerContainer


class TripHistoryScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "trip_history"
        self._page = 1
        self._has_more = True
        self._loading = False
        self._trips = []
        self._filter = "all"
        self._shimmer = None
        self._build_ui()

    def _build_ui(self):
        self.root = MDBoxLayout(orientation="vertical", md_bg_color="#F7F9FC")

        self.top_bar = MDTopAppBar(
            title="Historique",
            md_bg_color="#1A3A6C",
            specific_text_color="#FFFFFF",
            left_action_items=[["arrow-left", lambda x: self.go_back()]],
        )
        self.root.add_widget(self.top_bar)

        filter_bar = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(44),
            padding=[10, 0],
            spacing=4,
            md_bg_color="#FFFFFF",
        )
        filters = [
            ("all", "Tout"),
            ("today", "Aujourd hui"),
            ("week", "Cette semaine"),
            ("month", "Ce mois"),
        ]
        self.filter_buttons = {}
        for key, label_text in filters:
            btn = MDFlatButton(
                text=label_text,
                text_color="#1A3A6C" if key == "all" else "#718096",
                md_bg_color="#E8F0FE" if key == "all" else "#FFFFFF",
                size_hint_x=0.25,
                on_release=lambda x, k=key: self.change_filter(k),
            )
            self.filter_buttons[key] = btn
            filter_bar.add_widget(btn)
        self.root.add_widget(filter_bar)

        body = MDBoxLayout(orientation="vertical", padding=[0, 0])

        self.scroll = MDScrollView(size_hint=(1, 1))
        self.list_container = MDBoxLayout(
            orientation="vertical",
            padding=[16, 8],
            spacing=8,
            size_hint_y=None,
        )
        self.list_container.bind(minimum_height=self.list_container.setter("height"))
        self.scroll.add_widget(self.list_container)
        body.add_widget(self.scroll)

        self.shimmer_layout = MDBoxLayout(
            orientation="vertical",
            padding=[16, 8],
            spacing=8,
            size_hint_y=None,
        )
        self.shimmer_layout.bind(minimum_height=self.shimmer_layout.setter("height"))
        for _ in range(3):
            self.shimmer_layout.add_widget(ShimmerTripCard())
        self.shimmer_layout.opacity = 0
        body.add_widget(self.shimmer_layout)

        self.empty_state = MDBoxLayout(
            orientation="vertical",
            adaptive_size=True,
            pos_hint={"center_x": 0.5, "center_y": 0.5},
            opacity=0,
        )
        empty_icon = MDIconButton(
            icon="car-off",
            icon_color="#A0AEC0",
            theme_icon_size="Custom",
            icon_size=dp(64),
            pos_hint={"center_x": 0.5},
        )
        empty_label = MDLabel(
            text="Aucun trajet",
            font_style="Subtitle1",
            theme_text_color="Secondary",
            halign="center",
        )
        self.empty_state.add_widget(empty_icon)
        self.empty_state.add_widget(empty_label)
        body.add_widget(self.empty_state)

        self.spinner = MDSpinner(
            size_hint=(None, None),
            size=(dp(30), dp(30)),
            pos_hint={"center_x": 0.5},
            active=False,
        )
        body.add_widget(self.spinner)

        self.root.add_widget(body)
        self.add_widget(self.root)

    def go_back(self):
        self.manager.switch("home")

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

    def on_enter(self):
        self._page = 1
        self._trips = []
        self._has_more = True
        Clock.schedule_once(lambda dt: self.load_trips())

    def on_leave(self):
        if self._trips:
            cache_service.set("trips", {"trips": self._trips, "filter": self._filter})

    def change_filter(self, filter_key):
        self._filter = filter_key
        for key, btn in self.filter_buttons.items():
            btn.text_color = "#1A3A6C" if key == filter_key else "#718096"
            btn.md_bg_color = "#E8F0FE" if key == filter_key else "#FFFFFF"
        self._page = 1
        self._trips = []
        self._has_more = True
        Clock.schedule_once(lambda dt: self.load_trips())

    async def load_trips(self):
        if self._loading or not self._has_more:
            return
        self._loading = True
        self.spinner.active = True
        self.hide_offline_banner()
        if self._page == 1:
            self.shimmer_layout.opacity = 1
            self.list_container.opacity = 0
            self.empty_state.opacity = 0
            cached = cache_service.get("trips")
            if cached and cached.get("filter") == self._filter:
                Clock.schedule_once(lambda dt: self.render_trips(cached.get("trips", [])))
        try:
            params = {"page": self._page, "per_page": 20}
            if self._filter != "all":
                params["period"] = self._filter
            data = await api_client.get("/api/v1/trips", params=params)
            trips = data.get("trips", data.get("data", []))
            self._has_more = len(trips) >= 20
            Clock.schedule_once(lambda dt: self.render_trips(trips))
            Clock.schedule_once(lambda dt: self.hide_offline_banner())
        except Exception as e:
            if self._page == 1 and not cache_service.get("trips"):
                stale = cache_service.get_stale("trips")
                if stale:
                    Clock.schedule_once(lambda dt: self.render_trips(stale.get("trips", [])))
                    Clock.schedule_once(lambda dt: self.show_offline_banner())
                else:
                    Clock.schedule_once(lambda dt: self.show_error(str(e)))
        finally:
            self._loading = False
            Clock.schedule_once(lambda dt: setattr(self.spinner, "active", False))

    def render_trips(self, trips):
        if self._page == 1:
            self.list_container.clear_widgets()
            self.shimmer_layout.opacity = 0
            self.list_container.opacity = 1
        self._trips.extend(trips)
        for trip in trips:
            item = self._build_trip_item(trip)
            self.list_container.add_widget(item)
        self._page += 1
        is_empty = len(self._trips) == 0
        self.empty_state.opacity = 1 if is_empty else 0
        self.scroll.opacity = 0 if is_empty else 1

    def _build_trip_item(self, trip):
        time = trip.get("created_at", trip.get("date", "--"))[:16]
        route = f"{trip.get('origin', '--')} -> {trip.get('destination', '--')}"
        amount = f"{trip.get('price', '--')} XAF"
        status = trip.get("status", "completed")
        status_color = "#009E60"
        if status == "completed":
            status_label = "Termine"
        elif status == "cancelled":
            status_label = "Annule"
            status_color = "#E53E3E"
        else:
            status_label = status.capitalize()
            status_color = "#FCD116"

        card = MDCard(
            orientation="vertical",
            size_hint_y=None,
            height=dp(90),
            padding=[12, 8],
            spacing=4,
            md_bg_color="#FFFFFF",
            radius=[8],
        )

        row1 = MDBoxLayout(size_hint_y=None, height=dp(24))
        row1.add_widget(MDLabel(
            text=time,
            font_style="Caption",
            theme_text_color="Secondary",
            size_hint_x=0.3,
        ))
        row1.add_widget(MDLabel(
            text=status_label,
            font_style="Caption",
            theme_text_color="Custom",
            text_color=status_color,
            size_hint_x=0.7,
            halign="right",
            bold=True,
        ))
        card.add_widget(row1)

        card.add_widget(MDLabel(
            text=route,
            font_style="Subtitle2",
            theme_text_color="Primary",
            size_hint_y=None,
            height=dp(22),
        ))
        card.add_widget(MDLabel(
            text=amount,
            font_style="Body2",
            theme_text_color="Custom",
            text_color="#1A3A6C",
            bold=True,
            size_hint_y=None,
            height=dp(20),
        ))
        return card

    def show_error(self, message):
        MDSnackbar(text=f"Erreur: {message}", snackbar_x=10, snackbar_y=10).open()
