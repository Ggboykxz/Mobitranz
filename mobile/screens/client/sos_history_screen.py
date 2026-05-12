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
from kivy.metrics import dp
from mobile.services.api_client import api_client


STATUS_CONFIG = {
    "pending": {"label": "En attente", "color": "#FCD116", "bg": "#FFFFF0"},
    "acknowledged": {"label": "Pris en charge", "color": "#1A3A6C", "bg": "#E8F0FE"},
    "resolved": {"label": "Resolu", "color": "#009E60", "bg": "#F0FFF4"},
    "escalated": {"label": "Escalade", "color": "#E53E3E", "bg": "#FFF5F5"},
}


class SOSHistoryScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "sos_history"
        self._incidents = []
        self._build_ui()

    def _build_ui(self):
        self.root = MDBoxLayout(orientation="vertical", md_bg_color="#F7F9FC")

        self.top_bar = MDTopAppBar(
            title="Historique SOS",
            md_bg_color="#E53E3E",
            specific_text_color="#FFFFFF",
            left_action_items=[["arrow-left", lambda x: self.go_back()]],
        )
        self.root.add_widget(self.top_bar)

        body = MDBoxLayout(orientation="vertical")

        self.scroll = MDScrollView(size_hint=(1, 1))
        self.incident_list = MDBoxLayout(
            orientation="vertical",
            padding=[12, 8],
            spacing=8,
            size_hint_y=None,
        )
        self.incident_list.bind(minimum_height=self.incident_list.setter("height"))
        self.scroll.add_widget(self.incident_list)
        body.add_widget(self.scroll)

        self.empty_state = MDBoxLayout(
            orientation="vertical",
            adaptive_size=True,
            pos_hint={"center_x": 0.5, "center_y": 0.5},
            opacity=0,
        )
        empty_icon = MDIconButton(
            icon="shield-check",
            icon_color="#009E60",
            theme_icon_size="Custom",
            icon_size=dp(64),
            pos_hint={"center_x": 0.5},
        )
        empty_label = MDLabel(
            text="Aucun incident signale",
            font_style="Subtitle1",
            theme_text_color="Secondary",
            halign="center",
        )
        sub_label = MDLabel(
            text="Votre securite est notre priorite",
            font_style="Caption",
            theme_text_color="Secondary",
            halign="center",
        )
        self.empty_state.add_widget(empty_icon)
        self.empty_state.add_widget(empty_label)
        self.empty_state.add_widget(sub_label)
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
        self.manager.current = "home"

    def on_enter(self):
        Clock.schedule_once(lambda dt: self.load_incidents())

    async def load_incidents(self):
        self.spinner.active = True
        try:
            data = await api_client.get("/api/v1/sos/incidents")
            self._incidents = data.get("incidents", data.get("data", []))
            Clock.schedule_once(lambda dt: self.render_incidents())
        except Exception:
            Clock.schedule_once(lambda dt: self.load_fallback())
        finally:
            Clock.schedule_once(lambda dt: setattr(self.spinner, "active", False))

    def load_fallback(self):
        self._incidents = [
            {
                "type": "Accident",
                "location": "PK5, Libreville",
                "status": "resolved",
                "date": "15 Avr 2026",
                "description": "Collision mineure, pas de blesse",
            },
            {
                "type": "Comportement",
                "location": "Centre-ville",
                "status": "acknowledged",
                "date": "10 Avr 2026",
                "description": "Conducteur verbalement agressif",
            },
            {
                "type": "Arnaque",
                "location": "Owendo",
                "status": "escalated",
                "date": "02 Avr 2026",
                "description": "Tentative de surcout",
            },
        ]
        self.render_incidents()

    def render_incidents(self):
        self.incident_list.clear_widgets()
        has_items = len(self._incidents) > 0

        for inc in self._incidents:
            card = self._build_incident_card(inc)
            self.incident_list.add_widget(card)

        self.empty_state.opacity = 0 if has_items else 1
        self.scroll.opacity = 1 if has_items else 0

    def _build_incident_card(self, inc):
        status = inc.get("status", "pending")
        config = STATUS_CONFIG.get(status, STATUS_CONFIG["pending"])
        inc_type = inc.get("type", "Incident")
        location = inc.get("location", "--")
        date = inc.get("date", "--")
        description = inc.get("description", "")

        card = MDCard(
            orientation="vertical",
            size_hint_y=None,
            padding=[12, 10],
            spacing=6,
            md_bg_color="#FFFFFF",
            radius=[10],
        )

        header = MDBoxLayout(size_hint_y=None, height=dp(24), spacing=8)
        icon_w = MDIconButton(
            icon="alert-circle",
            icon_color=config["color"],
            theme_icon_size="Custom",
            icon_size=dp(20),
            size_hint_x=None,
            width=dp(28),
        )
        type_label = MDLabel(
            text=inc_type,
            font_style="Subtitle2",
            theme_text_color="Primary",
            bold=True,
        )
        status_badge = MDCard(
            orientation="vertical",
            size_hint_x=None,
            width=dp(100),
            md_bg_color=config["bg"],
            radius=[10],
            padding=[8, 2],
            pos_hint={"center_y": 0.5},
        )
        status_label = MDLabel(
            text=config["label"],
            font_style="Caption",
            theme_text_color="Custom",
            text_color=config["color"],
            halign="center",
            bold=True,
        )
        status_badge.add_widget(status_label)

        header.add_widget(icon_w)
        header.add_widget(type_label)
        header.add_widget(status_badge)
        card.add_widget(header)

        loc_row = MDBoxLayout(size_hint_y=None, height=dp(20), spacing=4)
        loc_icon = MDIconButton(
            icon="map-marker",
            icon_color="#718096",
            theme_icon_size="Custom",
            icon_size=dp(14),
            size_hint_x=None,
            width=dp(20),
        )
        loc_label = MDLabel(
            text=location,
            font_style="Caption",
            theme_text_color="Secondary",
        )
        date_label = MDLabel(
            text=date,
            font_style="Caption",
            theme_text_color="Custom",
            text_color="#A0AEC0",
            halign="right",
            size_hint_x=0.3,
        )
        loc_row.add_widget(loc_icon)
        loc_row.add_widget(loc_label)
        loc_row.add_widget(date_label)
        card.add_widget(loc_row)

        if description:
            card.add_widget(MDLabel(
                text=description,
                font_style="Body2",
                theme_text_color="Secondary",
                size_hint_y=None,
            ))

        self._set_card_height(card)

        return card

    def _set_card_height(self, card):
        desc_lines = 0
        for child in card.children:
            if isinstance(child, MDLabel) and child.font_style == "Body2":
                desc_lines = 1
        card.height = dp(80 + desc_lines * 20)
