from kivy.clock import Clock
from kivy.uix.screenmanager import Screen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton, MDFlatButton, MDIconButton
from kivymd.uix.spinner import MDSpinner
from kivymd.uix.snackbar import MDSnackbar
from kivymd.uix.topappbar import MDTopAppBar
from kivymd.uix.dialog import MDDialog
from kivy.metrics import dp
from mobile.services.api_client import api_client
from mobile.services.cache_service import cache_service
from mobile.ui.haptic import Haptic
from mobile.ui.ripple import RippleButton


class TripActiveScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "trip_active"
        self.trip_id = None
        self._poll_event = None
        self._dialog = None
        self._build_ui()

    def _build_ui(self):
        self.root = MDBoxLayout(orientation="vertical", md_bg_color="#F7F9FC")

        self.top_bar = MDTopAppBar(
            title="Trajet en cours",
            md_bg_color="#1A3A6C",
            specific_text_color="#FFFFFF",
            left_action_items=[["arrow-left", lambda x: self.go_back()]],
        )
        self.root.add_widget(self.top_bar)

        body = MDBoxLayout(orientation="vertical", padding=[20, 16], spacing=16)

        self.status_badge = MDCard(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(36),
            padding=[12, 6],
            md_bg_color="#C6F6D5",
            radius=[18],
            pos_hint={"center_x": 0.5},
        )
        self.status_label = MDLabel(
            text="EN COURS",
            font_style="Caption",
            theme_text_color="Custom",
            text_color="#009E60",
            bold=True,
        )
        self.status_badge.add_widget(self.status_label)
        body.add_widget(self.status_badge)

        self.map_card = MDCard(
            orientation="vertical",
            size_hint=(1, 0.35),
            md_bg_color="#E2E8F0",
            radius=[12],
            padding=0,
        )
        map_icon = MDIconButton(
            icon="map",
            icon_color="#718096",
            theme_icon_size="Custom",
            icon_size=dp(48),
            pos_hint={"center_x": 0.5, "center_y": 0.5},
        )
        map_label = MDLabel(
            text="Carte en temps reel",
            font_style="Body2",
            theme_text_color="Secondary",
            halign="center",
        )
        self.map_card.add_widget(map_icon)
        self.map_card.add_widget(map_label)
        body.add_widget(self.map_card)

        self.info_card = MDCard(
            orientation="vertical",
            size_hint_y=None,
            padding=16,
            spacing=8,
            md_bg_color="#FFFFFF",
            radius=[12],
        )
        self.driver_label = MDLabel(
            text="Conducteur: --",
            font_style="Subtitle2",
            theme_text_color="Primary",
        )
        self.vehicle_label = MDLabel(
            text="Vehicule: --",
            font_style="Body2",
            theme_text_color="Secondary",
        )
        self.eta_label = MDLabel(
            text="ETA: --",
            font_style="Body2",
            theme_text_color="Secondary",
        )
        self.dest_label = MDLabel(
            text="Destination: --",
            font_style="Body2",
            theme_text_color="Primary",
        )
        self.price_label = MDLabel(
            text="Prix: -- XAF",
            font_style="Body2",
            theme_text_color="Secondary",
        )
        self.info_card.add_widget(self.driver_label)
        self.info_card.add_widget(self.vehicle_label)
        self.info_card.add_widget(self.eta_label)
        self.info_card.add_widget(self.dest_label)
        self.info_card.add_widget(self.price_label)
        body.add_widget(self.info_card)

        self.sos_btn = RippleButton(
            text="SIGNALER UN INCIDENT",
            md_bg_color="#E53E3E",
            text_color="#FFFFFF",
            size_hint=(1, None),
            height=dp(52),
            on_release=self.report_incident,
        )
        body.add_widget(self.sos_btn)

        self.complete_btn = RippleButton(
            text="Terminer le trajet",
            md_bg_color="#009E60",
            text_color="#FFFFFF",
            size_hint=(1, None),
            height=dp(48),
            on_release=self.complete_trip,
        )
        body.add_widget(self.complete_btn)

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
        if self._poll_event:
            self._poll_event.cancel()
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
        self.trip_id = getattr(self, "trip_id", None) or getattr(self.manager, "current_trip_id", None)
        if self.trip_id:
            Clock.schedule_once(lambda dt: self.load_trip_data())
            self._poll_event = Clock.schedule_interval(lambda dt: self.poll_trip_status(), 15)

    def on_leave(self):
        if self._poll_event:
            self._poll_event.cancel()
            self._poll_event = None
        if hasattr(self, '_current_trip_data'):
            cache_service.set(f"trip_active_{self.trip_id}", self._current_trip_data)

    async def load_trip_data(self):
        self.spinner.active = True
        self.hide_offline_banner()
        cache_key = f"trip_active_{self.trip_id}"
        cached = cache_service.get(cache_key)
        if cached:
            self._current_trip_data = cached
            Clock.schedule_once(lambda dt: self.update_trip_info(cached))
        try:
            data = await api_client.get(f"/api/v1/trips/{self.trip_id}")
            self._current_trip_data = data
            cache_service.set(cache_key, data)
            Clock.schedule_once(lambda dt: self.update_trip_info(data))
            Clock.schedule_once(lambda dt: self.hide_offline_banner())
        except Exception as e:
            if not cached:
                stale = cache_service.get_stale(cache_key)
                if stale:
                    self._current_trip_data = stale
                    Clock.schedule_once(lambda dt: self.update_trip_info(stale))
                    Clock.schedule_once(lambda dt: self.show_offline_banner())
                else:
                    MDSnackbar(text=f"Erreur: {str(e)}", snackbar_x=10, snackbar_y=10).open()
        finally:
            Clock.schedule_once(lambda dt: setattr(self.spinner, "active", False))

    async def poll_trip_status(self):
        if not self.trip_id:
            return
        try:
            data = await api_client.get(f"/api/v1/trips/{self.trip_id}")
            Clock.schedule_once(lambda dt: self.update_trip_info(data))
        except Exception:
            pass

    def update_trip_info(self, data):
        driver = data.get("driver", {})
        vehicle = data.get("vehicle", {})
        self.driver_label.text = f"Conducteur: {driver.get('name', '--')}"
        self.vehicle_label.text = f"Vehicule: {vehicle.get('plate', '--')} ({vehicle.get('model', '--')})"
        self.eta_label.text = f"ETA: {data.get('eta', '--')} min"
        self.dest_label.text = f"Destination: {data.get('destination', '--')}"
        self.price_label.text = f"Prix: {data.get('price', '--')} XAF"
        status = data.get("status", "active")
        if status == "completed":
            self.status_label.text = "TERMINE"
            self.status_badge.md_bg_color = "#C6F6D5"
        elif status == "cancelled":
            self.status_label.text = "ANNULE"
            self.status_badge.md_bg_color = "#FED7D7"

    def report_incident(self, instance):
        if not self._dialog:
            self._dialog = MDDialog(
                title="Signaler un incident",
                text="Voulez-vous vraiment signaler un incident ? Un agent de securite sera alerte.",
                buttons=[
                    MDFlatButton(text="ANNULER", on_release=lambda x: self._dialog.dismiss()),
                    MDRaisedButton(
                        text="SIGNALER",
                        md_bg_color="#E53E3E",
                        on_release=self.submit_incident,
                    ),
                ],
            )
        self._dialog.open()

    def submit_incident(self, instance):
        self._dialog.dismiss()
        Clock.schedule_once(lambda dt: self.call_sos_api())

    async def call_sos_api(self):
        self.spinner.active = True
        try:
            result = await api_client.post("/api/v1/sos", {
                "trip_id": self.trip_id,
            })
            incident_id = result.get("incident_id")
            Haptic.heavy()
            MDSnackbar(
                text=f"Incident signale (Ref: {incident_id}). Secours en route.",
                snackbar_x=10,
                snackbar_y=10,
            ).open()
        except Exception as e:
            MDSnackbar(text=f"Erreur: {str(e)}", snackbar_x=10, snackbar_y=10).open()
        finally:
            self.spinner.active = False

    async def complete_trip(self, instance):
        self.spinner.active = True
        try:
            await api_client.post(f"/api/v1/trips/{self.trip_id}/complete", {})
            Haptic.heavy()
            MDSnackbar(text="Trajet termine !", snackbar_x=10, snackbar_y=10).open()
            Clock.schedule_once(lambda dt: self.go_to_rating(), 1)
        except Exception as e:
            Haptic.light()
            MDSnackbar(text=f"Erreur: {str(e)}", snackbar_x=10, snackbar_y=10).open()
        finally:
            self.spinner.active = False

    def go_to_rating(self):
        self.manager.switch("rating")
