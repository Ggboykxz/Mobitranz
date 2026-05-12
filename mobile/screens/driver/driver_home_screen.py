from kivy.clock import Clock
from kivy.metrics import dp
from kivy.properties import BooleanProperty
from kivymd.uix.screen import MDScreen
from kivymd.uix.card import MDCard
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.spinner import MDSpinner
from kivymd.uix.snackbar import MDSnackbar
from kivymd.uix.top_appbar import MDTopAppBar
from kivymd.uix.switch import MDSwitch
from mobile.theme.colors import Colors
from mobile.services.api_client import api_client
import asyncio


class DriverHomeScreen(MDScreen):
    _is_available = BooleanProperty(False)
    _loading = BooleanProperty(True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "driver_home"
        self._proposal_dialog = None
        self._poll_event = None
        self._build_ui()
        Clock.schedule_once(lambda dt: self._load_data(), 0.1)

    def _build_ui(self):
        layout = MDBoxLayout(orientation="vertical", spacing=dp(12))

        layout.add_widget(MDTopAppBar(
            title="MobiTranz",
            left_action_items=[["menu", lambda x: None]],
            right_action_items=[["account-circle", lambda x: self._go_to_profile()]],
            elevation=2
        ))

        scroll = MDBoxLayout(orientation="vertical", spacing=dp(12), padding=[dp(16), dp(8), dp(16), dp(16)])
        scroll.bind(minimum_height=scroll.setter("height"))
        scroll.size_hint_y = None
        scroll.height = 0

        self.status_card = MDCard(
            orientation="vertical",
            size_hint_y=None,
            height=dp(90),
            padding=dp(16),
            spacing=dp(12),
            radius=[dp(12)],
            elevation=2
        )
        status_row = MDBoxLayout(spacing=dp(12), adaptive_height=True)
        self.status_label = MDLabel(
            text="Hors service",
            theme_text_color="Custom",
            text_color=Colors.GREY_600,
            font_style="H6",
            adaptive_height=True
        )
        self.status_switch = MDSwitch(
            active=False,
            on_active=self._on_status_toggle,
            size_hint_x=None,
            width=dp(48)
        )
        status_row.add_widget(self.status_label)
        status_row.add_widget(MDBoxLayout())
        status_row.add_widget(self.status_switch)
        self.status_card.add_widget(status_row)
        scroll.add_widget(self.status_card)

        self.spinner = MDSpinner(
            size_hint=(None, None),
            size=(dp(32), dp(32)),
            pos_hint={"center_x": 0.5},
            active=True
        )
        scroll.add_widget(self.spinner)

        self.stats_grid = MDBoxLayout(
            spacing=dp(12),
            adaptive_height=True,
            pos_hint={"center_x": 0.5}
        )
        scroll.add_widget(self.stats_grid)

        proposal_header = MDLabel(
            text="Propositions",
            font_style="Subtitle1",
            theme_text_color="Secondary",
            adaptive_height=True
        )
        scroll.add_widget(proposal_header)

        self.proposal_card = MDCard(
            orientation="vertical",
            size_hint_y=None,
            height=dp(200),
            padding=dp(16),
            spacing=dp(8),
            radius=[dp(12)],
            elevation=2
        )
        self.proposal_card.md_bg_color = [1, 1, 1, 1]
        self.proposal_empty = MDLabel(
            text="Aucune proposition pour le moment",
            theme_text_color="Secondary",
            halign="center",
            adaptive_height=True
        )
        self.proposal_card.add_widget(self.proposal_empty)
        scroll.add_widget(self.proposal_card)

        outer_scroll = MDBoxLayout(orientation="vertical")
        outer_scroll.add_widget(scroll)
        layout.add_widget(outer_scroll)
        self.add_widget(layout)

    def _load_data(self):
        asyncio.ensure_future(self._fetch_stats())

    async def _fetch_stats(self):
        try:
            data = await api_client.get("/api/v1/driver/stats")
            Clock.schedule_once(lambda dt: self._update_stats(data))
        except Exception as e:
            Clock.schedule_once(lambda dt: self._show_error(str(e)))

    async def _fetch_proposals(self):
        try:
            data = await api_client.get("/api/v1/driver/proposals")
            Clock.schedule_once(lambda dt: self._update_proposals(data))
        except Exception:
            pass

    def _update_stats(self, data):
        self._loading = False
        self.spinner.active = False
        self.stats_grid.clear_widgets()

        is_available = data.get("is_available", False)
        self._is_available = is_available
        self.status_switch.active = is_available
        self.status_label.text = "En service" if is_available else "Hors service"
        self.status_label.theme_text_color = "Custom"
        self.status_label.text_color = Colors.ACCENT if is_available else Colors.GREY_600
        self.status_card.md_bg_color = [0.9, 1, 0.92, 1] if is_available else [0.95, 0.95, 0.95, 1]

        stats = data.get("stats", {})
        items = [
            ("calendar-today", str(stats.get("trips_today", 0)), "Trajets"),
            ("cash", f"{stats.get('earnings_today', 0):,} XAF", "Revenus"),
            ("star", str(stats.get("rating", 0)), "Note"),
        ]
        for icon, value, label in items:
            card = MDCard(
                orientation="vertical",
                size_hint=(0.3, None),
                height=dp(90),
                padding=dp(8),
                spacing=dp(4),
                radius=[dp(8)],
                elevation=1
            )
            card.add_widget(MDLabel(
                text=icon,
                font_style="H5",
                halign="center",
                adaptive_height=True
            ))
            card.add_widget(MDLabel(
                text=value,
                font_style="H6",
                halign="center",
                bold=True,
                adaptive_height=True,
                theme_text_color="Primary"
            ))
            card.add_widget(MDLabel(
                text=label,
                font_style="Caption",
                halign="center",
                adaptive_height=True,
                theme_text_color="Secondary"
            ))
            self.stats_grid.add_widget(card)

        if data.get("proposal"):
            Clock.schedule_once(lambda dt: self._show_proposal(data["proposal"]))

    def _update_proposals(self, data):
        proposals = data if isinstance(data, list) else data.get("proposals", [])
        if proposals:
            self._show_proposal(proposals[0])

    def _show_proposal(self, proposal):
        self.proposal_card.clear_widgets()
        self.proposal_card.md_bg_color = [1, 1, 1, 1]

        pickup = proposal.get("pickup_location", "Inconnu")
        destination = proposal.get("destination", "Inconnu")
        price = proposal.get("price", 0)
        seats = proposal.get("seats_available", 1)
        client = proposal.get("client_name", proposal.get("passenger_name", "Client"))

        self.proposal_card.add_widget(MDLabel(
            text=f"{pickup}  \u2192  {destination}",
            font_style="Subtitle1",
            bold=True,
            adaptive_height=True
        ))
        self.proposal_card.add_widget(MDLabel(
            text=f"{price:,} XAF \u00b7 {seats} place(s)",
            font_style="Body1",
            theme_text_color="Secondary",
            adaptive_height=True
        ))
        self.proposal_card.add_widget(MDLabel(
            text=f"Client: {client}",
            font_style="Body2",
            theme_text_color="Secondary",
            adaptive_height=True
        ))

        btn_row = MDBoxLayout(spacing=dp(12), adaptive_height=True, pos_hint={"center_x": 0.5})
        accept_btn = MDRaisedButton(
            text="Accepter",
            md_bg_color=Colors.ACCENT_BG,
            on_release=lambda x: self._accept_proposal(proposal),
            size_hint_x=0.4
        )
        reject_btn = MDFlatButton(
            text="Refuser",
            theme_text_color="Custom",
            text_color=Colors.DANGER,
            on_release=lambda x: self._reject_proposal(proposal),
            size_hint_x=0.4
        )
        btn_row.add_widget(accept_btn)
        btn_row.add_widget(reject_btn)
        self.proposal_card.add_widget(btn_row)

    def _on_status_toggle(self, instance, active):
        self._is_available = active
        asyncio.ensure_future(self._update_status(active))

    async def _update_status(self, active):
        try:
            data = await api_client.post("/api/v1/driver/status", {"is_available": active})
            Clock.schedule_once(lambda dt: self._on_status_updated(data))
        except Exception as e:
            Clock.schedule_once(lambda dt: self._revert_status(str(e)))

    def _on_status_updated(self, data):
        self.status_label.text = "En service" if self._is_available else "Hors service"
        self.status_label.text_color = Colors.ACCENT if self._is_available else Colors.GREY_600
        self.status_card.md_bg_color = [0.9, 1, 0.92, 1] if self._is_available else [0.95, 0.95, 0.95, 1]
        if self._is_available and not self._poll_event:
            self._poll_event = Clock.schedule_interval(lambda dt: self._poll_proposals(), 10)

    def _revert_status(self, error_msg):
        self._is_available = not self._is_available
        self.status_switch.active = self._is_available
        self._show_snackbar(f"Erreur: {error_msg}")

    def _poll_proposals(self):
        asyncio.ensure_future(self._fetch_proposals())

    def _accept_proposal(self, proposal):
        proposal_id = proposal.get("id")
        asyncio.ensure_future(self._send_proposal_response(proposal_id, "accept"))

    def _reject_proposal(self, proposal):
        proposal_id = proposal.get("id")
        asyncio.ensure_future(self._send_proposal_response(proposal_id, "reject"))

    async def _send_proposal_response(self, proposal_id, action):
        try:
            if action == "accept":
                data = await api_client.post(f"/api/v1/driver/proposals/{proposal_id}/accept", {})
                Clock.schedule_once(lambda dt: self._on_accepted(data))
            else:
                await api_client.post(f"/api/v1/driver/proposals/{proposal_id}/reject", {})
                Clock.schedule_once(lambda dt: self._on_rejected())
        except Exception as e:
            Clock.schedule_once(lambda dt: self._show_error(str(e)))

    def _on_accepted(self, data):
        self._show_snackbar("Proposition acceptee! Trajet en cours.")
        trip_id = data.get("trip_id", data.get("id"))
        if trip_id:
            self.manager.get_screen("trip_active_driver").trip_id = str(trip_id)
            self.manager.current = "trip_active_driver"

    def _on_rejected(self):
        self._show_snackbar("Proposition refusee")
        self._reset_proposals()

    def _reset_proposals(self):
        self.proposal_card.clear_widgets()
        self.proposal_card.add_widget(self.proposal_empty)

    def _show_error(self, message):
        self._loading = False
        self.spinner.active = False
        self._show_snackbar(f"Erreur: {message}")

    def _show_snackbar(self, text):
        MDSnackbar(text=text, y=dp(24)).open()

    def _go_to_profile(self):
        self.manager.current = "profile"

    def on_leave(self):
        if self._poll_event:
            self._poll_event.cancel()
            self._poll_event = None

    def on_enter(self):
        Clock.schedule_once(lambda dt: self._load_data(), 0.1)
        if self._is_available and not self._poll_event:
            self._poll_event = Clock.schedule_interval(lambda dt: self._poll_proposals(), 10)
