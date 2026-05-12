from kivy.clock import Clock
from kivy.metrics import dp
from kivy.properties import StringProperty
from kivymd.uix.screen import MDScreen
from kivymd.uix.card import MDCard
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.spinner import MDSpinner
from kivymd.uix.snackbar import MDSnackbar
from kivymd.uix.top_appbar import MDTopAppBar
from kivymd.uix.dialog import MDDialog
from mobile.theme.colors import Colors
from mobile.services.api_client import api_client
from mobile.services.cache_service import cache_service
from mobile.config import DEFAULT_LOCATION
import asyncio


class TripActiveDriverScreen(MDScreen):
    trip_id = StringProperty("")
    _loading = True
    _camera_active = False
    _location_event = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "trip_active_driver"
        self._build_ui()

    def _build_ui(self):
        layout = MDBoxLayout(orientation="vertical", spacing=dp(8))

        layout.add_widget(MDTopAppBar(
            title="Trajet en cours",
            left_action_items=[["arrow-left", lambda x: self._confirm_cancel()]],
            elevation=2
        ))

        scroll = MDBoxLayout(orientation="vertical", spacing=dp(12), padding=[dp(16), dp(8), dp(16), dp(16)])
        scroll.bind(minimum_height=scroll.setter("height"))
        scroll.size_hint_y = None
        scroll.height = 0

        self.spinner = MDSpinner(
            size_hint=(None, None),
            size=(dp(32), dp(32)),
            pos_hint={"center_x": 0.5},
            active=True
        )
        scroll.add_widget(self.spinner)

        self.status_banner = MDCard(
            orientation="vertical",
            size_hint_y=None,
            height=dp(60),
            padding=dp(12),
            radius=[dp(8)],
            elevation=1
        )
        self.status_banner.md_bg_color = [0.9, 1, 0.92, 1]
        self.status_label = MDLabel(
            text="TRAJET EN COURS",
            font_style="H6",
            halign="center",
            theme_text_color="Custom",
            text_color=Colors.ACCENT,
            adaptive_height=True
        )
        self.status_banner.add_widget(self.status_label)
        scroll.add_widget(self.status_banner)

        self.info_card = MDCard(
            orientation="vertical",
            size_hint_y=None,
            height=dp(160),
            padding=dp(16),
            spacing=dp(8),
            radius=[dp(12)],
            elevation=2
        )
        self.info_card.md_bg_color = [1, 1, 1, 1]
        self.client_label = MDLabel(
            text="Client: --",
            font_style="H6",
            bold=True,
            adaptive_height=True
        )
        self.pickup_label = MDLabel(
            text="",
            font_style="Body1",
            theme_text_color="Secondary",
            adaptive_height=True
        )
        self.dest_label = MDLabel(
            text="",
            font_style="Body1",
            theme_text_color="Secondary",
            adaptive_height=True
        )
        self.price_label = MDLabel(
            text="",
            font_style="Body1",
            theme_text_color="Primary",
            adaptive_height=True
        )
        self.info_card.add_widget(self.client_label)
        self.info_card.add_widget(self.pickup_label)
        self.info_card.add_widget(self.dest_label)
        self.info_card.add_widget(self.price_label)
        scroll.add_widget(self.info_card)

        self.gps_card = MDCard(
            orientation="vertical",
            size_hint_y=None,
            height=dp(80),
            padding=dp(12),
            spacing=dp(4),
            radius=[dp(12)],
            elevation=1
        )
        self.gps_card.md_bg_color = [0.95, 0.97, 1, 1]
        self.gps_card.add_widget(MDLabel(
            text="gps-fixed",
            font_style="H5",
            halign="center",
            adaptive_height=True
        ))
        self.gps_label = MDLabel(
            text="Localisation GPS active",
            font_style="Caption",
            halign="center",
            adaptive_height=True,
            theme_text_color="Secondary"
        )
        self.gps_card.add_widget(self.gps_label)
        scroll.add_widget(self.gps_card)

        self.camera_btn = MDRaisedButton(
            text="videocam-off  Camera: OFF",
            size_hint_y=None,
            height=dp(48),
            md_bg_color=Colors.GREY_400,
            on_release=self._toggle_camera
        )
        scroll.add_widget(self.camera_btn)

        btn_row = MDBoxLayout(spacing=dp(12), adaptive_height=True)
        sos_btn = MDRaisedButton(
            text="alert  SOS",
            md_bg_color=Colors.DANGER,
            on_release=self._trigger_sos,
            size_hint_x=0.5
        )
        complete_btn = MDRaisedButton(
            text="check  Terminer",
            md_bg_color=Colors.ACCENT_BG,
            on_release=self._confirm_complete,
            size_hint_x=0.5
        )
        btn_row.add_widget(sos_btn)
        btn_row.add_widget(complete_btn)
        scroll.add_widget(btn_row)

        layout.add_widget(scroll)
        self.add_widget(layout)

    def on_enter(self):
        if self.trip_id:
            Clock.schedule_once(lambda dt: self._load_trip(), 0.1)

    def on_leave(self):
        if self._location_event:
            self._location_event.cancel()
            self._location_event = None

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

    def _load_trip(self):
        self._loading = True
        self.spinner.active = True
        asyncio.ensure_future(self._fetch_trip())

    async def _fetch_trip(self):
        self.hide_offline_banner()
        cache_key = f"trip_driver_{self.trip_id}"
        cached = cache_service.get(cache_key)
        if cached:
            Clock.schedule_once(lambda dt: self._update_trip(cached))
        try:
            data = await api_client.get(f"/api/v1/trips/{self.trip_id}")
            cache_service.set(cache_key, data)
            Clock.schedule_once(lambda dt: self._update_trip(data))
            Clock.schedule_once(lambda dt: self.hide_offline_banner())
        except Exception as e:
            if not cached:
                stale = cache_service.get_stale(cache_key)
                if stale:
                    Clock.schedule_once(lambda dt: self._update_trip(stale))
                    Clock.schedule_once(lambda dt: self.show_offline_banner())
                else:
                    Clock.schedule_once(lambda dt: self._show_error(str(e)))

    def _update_trip(self, data):
        self._loading = False
        self.spinner.active = False

        client_name = data.get("passenger_name", data.get("client_name", "Client"))
        pickup = data.get("pickup_location", "")
        destination = data.get("destination", data.get("dropoff_location", ""))
        price = data.get("price", data.get("amount", 0))
        seats = data.get("seats_available", 1)

        self.client_label.text = f"Client: {client_name}"
        self.pickup_label.text = f"Depuis: {pickup}"
        self.dest_label.text = f"Destination: {destination}"
        self.price_label.text = f"{price:,} XAF \u00b7 {seats} place(s)"

        self._start_location_updates()

    def _start_location_updates(self):
        if self._location_event:
            self._location_event.cancel()
        self._location_event = Clock.schedule_interval(lambda dt: self._send_location(), 5)

    def _send_location(self):
        lat = DEFAULT_LOCATION["lat"]
        lon = DEFAULT_LOCATION["lon"]
        asyncio.ensure_future(self._post_location(lat, lon))

    async def _post_location(self, lat, lon):
        try:
            await api_client.post(f"/api/v1/trips/{self.trip_id}/location", {
                "latitude": lat,
                "longitude": lon
            })
        except Exception:
            pass

    def _toggle_camera(self, instance):
        self._camera_active = not self._camera_active
        if self._camera_active:
            instance.text = "videocam  Camera: ON"
            instance.md_bg_color = Colors.ACCENT_BG
            self._show_snackbar("Camera activee")
        else:
            instance.text = "videocam-off  Camera: OFF"
            instance.md_bg_color = Colors.GREY_400
            self._show_snackbar("Camera desactivee")

    def _trigger_sos(self, instance):
        asyncio.ensure_future(self._send_sos())

    async def _send_sos(self):
        try:
            await api_client.post(f"/api/v1/trips/{self.trip_id}/sos", {
                "latitude": DEFAULT_LOCATION["lat"],
                "longitude": DEFAULT_LOCATION["lon"]
            })
            Clock.schedule_once(lambda dt: self._show_snackbar("Alerte SOS envoyee"))
        except Exception as e:
            Clock.schedule_once(lambda dt: self._show_error(str(e)))

    def _confirm_complete(self, instance):
        self._dialog = MDDialog(
            title="Terminer le trajet",
            text="Voulez-vous vraiment terminer ce trajet?",
            buttons=[
                MDFlatButton(text="Annuler", on_release=lambda x: self._dialog.dismiss()),
                MDRaisedButton(
                    text="Terminer",
                    md_bg_color=Colors.ACCENT_BG,
                    on_release=lambda x: self._complete_trip()
                ),
            ]
        )
        self._dialog.open()

    def _confirm_cancel(self):
        self._dialog = MDDialog(
            title="Quitter le trajet",
            text="Voulez-vous vraiment quitter cet ecran?",
            buttons=[
                MDFlatButton(text="Rester", on_release=lambda x: self._dialog.dismiss()),
                MDRaisedButton(
                    text="Quitter",
                    md_bg_color=Colors.DANGER,
                    on_release=lambda x: self._do_leave()
                ),
            ]
        )
        self._dialog.open()

    def _do_leave(self):
        if self._dialog:
            self._dialog.dismiss()
        if self._location_event:
            self._location_event.cancel()
            self._location_event = None
        self.manager.switch("driver_home")

    def _complete_trip(self):
        if self._dialog:
            self._dialog.dismiss()
        asyncio.ensure_future(self._complete_trip_api())

    async def _complete_trip_api(self):
        try:
            await api_client.post(f"/api/v1/trips/{self.trip_id}/complete", {})
            Clock.schedule_once(lambda dt: self._on_complete_success())
        except Exception as e:
            Clock.schedule_once(lambda dt: self._show_error(str(e)))

    def _on_complete_success(self):
        if self._location_event:
            self._location_event.cancel()
            self._location_event = None
        self._show_snackbar("Trajet termine avec succes")
        self.trip_id = ""
        self.manager.switch("driver_home")

    def _show_error(self, message):
        self._loading = False
        self.spinner.active = False
        self._show_snackbar(f"Erreur: {message}")

    def _show_snackbar(self, text):
        MDSnackbar(text=text, y=dp(24)).open()
