from kivy.clock import Clock
from kivy.uix.screenmanager import Screen
from kivy.graphics import Color, RoundedRectangle
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton, MDFlatButton, MDIconButton
from kivymd.uix.spinner import MDSpinner
from kivymd.uix.snackbar import MDSnackbar
from kivymd.uix.topappbar import MDTopAppBar
from kivy.metrics import dp
from mobile.services.api_client import api_client
from mobile.config import DEFAULT_LOCATION


class MapScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "map"
        self.user_lat = DEFAULT_LOCATION["lat"]
        self.user_lon = DEFAULT_LOCATION["lon"]
        self._map_view = None
        self._build_ui()

    def _build_ui(self):
        self.root = MDBoxLayout(orientation="vertical", md_bg_color="#F7F9FC")

        self.top_bar = MDTopAppBar(
            title="Carte",
            md_bg_color="#1A3A6C",
            specific_text_color="#FFFFFF",
            left_action_items=[["arrow-left", lambda x: self.go_back()]],
            right_action_items=[["crosshairs-gps", lambda x: self.locate_user()]],
        )
        self.root.add_widget(self.top_bar)

        self.map_container = MDBoxLayout(
            orientation="vertical",
            size_hint=(1, 0.55),
            md_bg_color="#E2E8F0",
        )

        self._try_mapview()

        info_panel = MDBoxLayout(
            orientation="vertical",
            size_hint_y=None,
            padding=[16, 12],
            spacing=8,
            md_bg_color="#FFFFFF",
        )

        self.position_card = MDCard(
            orientation="vertical",
            size_hint_y=None,
            height=dp(50),
            padding=[12, 6],
            md_bg_color="#F7FAFC",
            radius=[8],
        )
        self.position_label = MDLabel(
            text=f"Position: {self.user_lat}, {self.user_lon}",
            font_style="Body2",
            theme_text_color="Primary",
        )
        self.position_card.add_widget(self.position_label)
        info_panel.add_widget(self.position_card)

        self.drivers_card = MDCard(
            orientation="vertical",
            size_hint_y=None,
            height=dp(60),
            padding=[12, 6],
            md_bg_color="#F7FAFC",
            radius=[8],
        )
        self.drivers_info = MDLabel(
            text="Chauffeurs proches: --",
            font_style="Body2",
            theme_text_color="Secondary",
        )
        self.drivers_card.add_widget(self.drivers_info)
        info_panel.add_widget(self.drivers_card)

        self.zones_card = MDCard(
            orientation="vertical",
            size_hint_y=None,
            height=dp(60),
            padding=[12, 6],
            md_bg_color="#F7FAFC",
            radius=[8],
        )
        self.zones_label = MDLabel(
            text="Zone tarifaire: --",
            font_style="Body2",
            theme_text_color="Secondary",
        )
        self.zones_card.add_widget(self.zones_label)
        info_panel.add_widget(self.zones_card)

        self.root.add_widget(info_panel)

        button_bar = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(56),
            padding=[16, 8],
            spacing=12,
            md_bg_color="#FFFFFF",
        )

        locate_btn = MDRaisedButton(
            text="Me localiser",
            md_bg_color="#009E60",
            text_color="#FFFFFF",
            size_hint_x=0.5,
            on_release=self.locate_user,
        )
        search_btn = MDRaisedButton(
            text="Rechercher",
            md_bg_color="#FCD116",
            text_color="#1A202C",
            size_hint_x=0.5,
            on_release=self.search_location,
        )
        button_bar.add_widget(locate_btn)
        button_bar.add_widget(search_btn)
        self.root.add_widget(button_bar)

        self.spinner = MDSpinner(
            size_hint=(None, None),
            size=(dp(30), dp(30)),
            pos_hint={"center_x": 0.5},
            active=False,
        )
        self.root.add_widget(self.spinner)

        self.add_widget(self.root)

    def _try_mapview(self):
        try:
            from kivy_garden.mapview import MapView, MapMarker
            self._map_view = MapView(
                lat=self.user_lat,
                lon=self.user_lon,
                zoom=13,
            )
            marker = MapMarker(lat=self.user_lat, lon=self.user_lon)
            self._map_view.add_widget(marker)
            self.map_container.clear_widgets()
            self.map_container.add_widget(self._map_view)
        except ImportError:
            self._show_map_placeholder()

    def _show_map_placeholder(self):
        placeholder = MDBoxLayout(
            orientation="vertical",
            adaptive_size=True,
            pos_hint={"center_x": 0.5, "center_y": 0.5},
        )
        icon = MDIconButton(
            icon="map",
            icon_color="#718096",
            theme_icon_size="Custom",
            icon_size=dp(64),
            pos_hint={"center_x": 0.5},
        )
        label = MDLabel(
            text=f"Carte MobiTranz\nPosition: {self.user_lat}, {self.user_lon}\nLibreville, Gabon",
            font_style="Body1",
            theme_text_color="Secondary",
            halign="center",
        )
        placeholder.add_widget(icon)
        placeholder.add_widget(label)
        self.map_container.clear_widgets()
        self.map_container.add_widget(placeholder)

    def go_back(self):
        self.manager.current = "home"

    def on_enter(self):
        Clock.schedule_once(lambda dt: self.refresh_data())

    async def refresh_data(self):
        self.spinner.active = True
        try:
            data = await api_client.get("/api/v1/map", params={
                "lat": self.user_lat,
                "lon": self.user_lon,
            })
            Clock.schedule_once(lambda dt: self.update_map_data(data))
        except Exception:
            Clock.schedule_once(lambda dt: self.set_default_data())
        finally:
            Clock.schedule_once(lambda dt: setattr(self.spinner, "active", False))

    def update_map_data(self, data):
        drivers = data.get("drivers", data.get("nearby_drivers", []))
        zones = data.get("zones", data.get("fare_zones", []))

        driver_count = len(drivers)
        self.drivers_info.text = f"Chauffeurs proches: {driver_count} disponible{'s' if driver_count != 1 else ''}"

        if zones:
            zone = zones[0]
            zone_name = zone.get("name", "--")
            zone_price = zone.get("price", zone.get("base_fare", "--"))
            self.zones_label.text = f"Zone tarifaire: {zone_name} - {zone_price} XAF"

        if drivers and self._map_view:
            try:
                from kivy_garden.mapview import MapMarker
                for d in drivers:
                    lat = d.get("lat", d.get("latitude"))
                    lon = d.get("lon", d.get("longitude"))
                    if lat and lon:
                        marker = MapMarker(lat=lat, lon=lon, source="car.png")
                        self._map_view.add_widget(marker)
            except ImportError:
                pass

    def set_default_data(self):
        self.drivers_info.text = "Chauffeurs proches: Donnees non disponibles"
        self.zones_label.text = "Zone tarifaire: Centre Ville - 500 XAF"

    def locate_user(self, instance=None):
        self.position_label.text = "Localisation en cours..."
        Clock.schedule_once(lambda dt: self._update_position())

    def _update_position(self):
        self.position_label.text = f"Position: {self.user_lat}, {self.user_lon}"
        MDSnackbar(text="Position mise a jour", snackbar_x=10, snackbar_y=10).open()

    def search_location(self, instance):
        MDSnackbar(
            text="Recherche de position - Saisissez votre destination",
            snackbar_x=10,
            snackbar_y=10,
        ).open()

    def update_location(self, lat, lon):
        self.user_lat = lat
        self.user_lon = lon
        self.position_label.text = f"Position: {lat}, {lon}"

        if self._map_view:
            try:
                self._map_view.center_on(lat, lon)
            except Exception:
                pass

        Clock.schedule_once(lambda dt: self.refresh_data())
