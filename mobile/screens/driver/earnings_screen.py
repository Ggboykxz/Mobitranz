from kivy.clock import Clock
from kivy.metrics import dp
from kivy.properties import StringProperty, BooleanProperty
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.card import MDCard
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.spinner import MDSpinner
from kivymd.uix.snackbar import MDSnackbar
from kivymd.uix.top_appbar import MDTopAppBar
from kivymd.uix.scrollview import MDScrollView
from mobile.theme.colors import Colors
from mobile.services.api_client import api_client
import asyncio


class EarningsScreen(MDScreen):
    _period = StringProperty("today")
    _loading = BooleanProperty(True)
    _driver_id = StringProperty("")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "earnings"
        self._build_ui()

    def _build_ui(self):
        layout = MDBoxLayout(orientation="vertical", spacing=dp(8))

        layout.add_widget(MDTopAppBar(
            title="Revenus",
            left_action_items=[["arrow-left", lambda x: self._go_back()]],
            right_action_items=[["refresh", lambda x: self._refresh()]],
            elevation=2
        ))

        scroll = MDScrollView()
        content = MDBoxLayout(
            orientation="vertical",
            spacing=dp(12),
            padding=[dp(16), dp(8), dp(16), dp(16)],
            adaptive_height=True
        )

        self.spinner = MDSpinner(
            size_hint=(None, None),
            size=(dp(36), dp(36)),
            pos_hint={"center_x": 0.5},
            active=True
        )
        content.add_widget(self.spinner)

        self.total_card = MDCard(
            orientation="vertical",
            size_hint_y=None,
            height=dp(130),
            padding=dp(20),
            spacing=dp(8),
            radius=[dp(16)],
            elevation=3
        )
        self.total_card.md_bg_color = Colors.PRIMARY_BG
        self.total_card.add_widget(MDLabel(
            text="AUJOURD'HUI",
            font_style="Caption",
            halign="center",
            theme_text_color="Custom",
            text_color=[1, 1, 1, 0.7],
            adaptive_height=True
        ))
        self.total_amount = MDLabel(
            text="0 XAF",
            font_style="H3",
            halign="center",
            theme_text_color="Custom",
            text_color=[1, 1, 1, 1],
            adaptive_height=True
        )
        self.total_card.add_widget(self.total_amount)
        content.add_widget(self.total_card)

        period_row = MDBoxLayout(spacing=dp(8), adaptive_height=True, pos_hint={"center_x": 0.5})
        periods = [
            ("today", "Aujourd'hui"),
            ("week", "Cette semaine"),
            ("month", "Ce mois"),
            ("year", "Cette annee"),
        ]
        self._period_buttons = {}
        for key, label in periods:
            btn = MDRaisedButton(
                text=label,
                size_hint=(0.22, None),
                height=dp(36),
                md_bg_color=Colors.ACCENT_BG if key == "today" else [0.9, 0.9, 0.9, 1],
                text_color=[1, 1, 1, 1] if key == "today" else Colors.GREY_700,
                on_release=lambda x, k=key: self._switch_period(k)
            )
            self._period_buttons[key] = btn
            period_row.add_widget(btn)
        content.add_widget(period_row)

        self.stats_grid = MDBoxLayout(spacing=dp(12), adaptive_height=True)
        content.add_widget(self.stats_grid)

        content.add_widget(MDLabel(
            text="Historique des transactions",
            font_style="Subtitle1",
            theme_text_color="Secondary",
            adaptive_height=True
        ))

        self.transaction_container = MDBoxLayout(
            orientation="vertical",
            spacing=dp(6),
            adaptive_height=True
        )
        content.add_widget(self.transaction_container)

        self.empty_label = MDLabel(
            text="Aucune transaction",
            font_style="Body1",
            theme_text_color="Secondary",
            halign="center",
            adaptive_height=True
        )
        content.add_widget(self.empty_label)
        self.empty_label.opacity = 0

        withdraw_btn = MDRaisedButton(
            text="credit-card  Retirer mes gains",
            size_hint_y=None,
            height=dp(56),
            md_bg_color=Colors.ACCENT_BG,
            on_release=self._withdraw
        )
        content.add_widget(withdraw_btn)

        scroll.add_widget(content)
        layout.add_widget(scroll)
        self.add_widget(layout)

    def on_enter(self):
        Clock.schedule_once(lambda dt: self._load_data(), 0.1)

    def _refresh(self):
        self._load_data()

    def _load_data(self):
        self._loading = True
        self.spinner.active = True
        asyncio.ensure_future(self._fetch_earnings())

    def _switch_period(self, period):
        self._period = period
        for key, btn in self._period_buttons.items():
            if key == period:
                btn.md_bg_color = Colors.ACCENT_BG
                btn.text_color = [1, 1, 1, 1]
            else:
                btn.md_bg_color = [0.9, 0.9, 0.9, 1]
                btn.text_color = Colors.GREY_700
        self._load_data()

    async def _fetch_earnings(self):
        try:
            app = MDApp.get_running_app()
            driver_id = getattr(app, "driver_id", "")
            if not driver_id:
                driver_id = "me"
            data = await api_client.get(f"/api/v1/payments", params={"driver_id": driver_id, "period": self._period})
            Clock.schedule_once(lambda dt: self._update_earnings(data))
        except Exception as e:
            Clock.schedule_once(lambda dt: self._show_error(str(e)))

    def _update_earnings(self, data):
        self._loading = False
        self.spinner.active = False

        period_labels = {
            "today": "AUJOURD'HUI",
            "week": "CETTE SEMAINE",
            "month": "CE MOIS",
            "year": "CETTE ANNEE",
        }
        period_text = period_labels.get(self._period, "AUJOURD'HUI")
        self.total_card.clear_widgets()
        self.total_card.add_widget(MDLabel(
            text=period_text,
            font_style="Caption",
            halign="center",
            theme_text_color="Custom",
            text_color=[1, 1, 1, 0.7],
            adaptive_height=True
        ))
        total = data.get("total", data.get("total_earnings", 0))
        self.total_amount.text = f"{total:,} XAF" if isinstance(total, (int, float)) else str(total)
        self.total_card.add_widget(self.total_amount)

        stats = data.get("stats", data.get("summary", {}))
        self.stats_grid.clear_widgets()
        stat_items = [
            ("directions-car", str(stats.get("trips_count", stats.get("count", 0))), "Trajets"),
            ("cash-multiple", f"{stats.get('total_earnings', stats.get('total', 0)):,} XAF", "Total"),
            ("star", str(stats.get("avg_rating", stats.get("rating", "0"))), "Note"),
        ]
        for icon, value, label in stat_items:
            card = MDCard(
                orientation="vertical",
                size_hint=(0.3, None),
                height=dp(80),
                padding=dp(8),
                spacing=dp(2),
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
                font_style="Subtitle1",
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

        transactions = data.get("transactions", data.get("history", []))
        self.transaction_container.clear_widgets()
        if not transactions:
            self.empty_label.opacity = 1
        else:
            self.empty_label.opacity = 0
            for txn in transactions:
                date = txn.get("date", txn.get("created_at", ""))
                desc = txn.get("description", txn.get("type", "Trajet"))
                amount = txn.get("amount", 0)
                sign = "+" if isinstance(amount, (int, float)) and amount >= 0 else ""
                amount_str = f"{sign}{amount:,} XAF" if isinstance(amount, (int, float)) else str(amount)
                is_positive = isinstance(amount, (int, float)) and amount >= 0

                txn_card = MDCard(
                    orientation="vertical",
                    size_hint_y=None,
                    height=dp(60),
                    padding=[dp(12), dp(8)],
                    spacing=dp(4),
                    radius=[dp(8)],
                    elevation=1
                )
                txn_card.add_widget(MDLabel(
                    text=desc,
                    font_style="Body1",
                    adaptive_height=True,
                    theme_text_color="Primary"
                ))
                detail_row = MDBoxLayout(adaptive_height=True, spacing=dp(8))
                detail_row.add_widget(MDLabel(
                    text=date if isinstance(date, str) else str(date),
                    font_style="Caption",
                    adaptive_height=True,
                    theme_text_color="Secondary",
                    size_hint_x=0.6
                ))
                detail_row.add_widget(MDLabel(
                    text=amount_str,
                    font_style="Caption",
                    adaptive_height=True,
                    theme_text_color="Custom",
                    text_color=Colors.ACCENT if is_positive else Colors.DANGER,
                    size_hint_x=0.4,
                    halign="right"
                ))
                txn_card.add_widget(detail_row)
                self.transaction_container.add_widget(txn_card)

    def _withdraw(self, instance):
        asyncio.ensure_future(self._do_withdraw())

    async def _do_withdraw(self):
        try:
            app = MDApp.get_running_app()
            driver_id = getattr(app, "driver_id", "")
            data = await api_client.post("/api/v1/payments/withdraw", {"driver_id": driver_id})
            Clock.schedule_once(lambda dt: self._show_snackbar(
                f"Retrait reussi! {data.get('amount', 0):,} XAF"
            ))
            Clock.schedule_once(lambda dt: self._load_data(), 0.5)
        except Exception as e:
            Clock.schedule_once(lambda dt: self._show_error(str(e)))

    def _show_error(self, message):
        self._loading = False
        self.spinner.active = False
        self._show_snackbar(f"Erreur: {message}")

    def _show_snackbar(self, text):
        MDSnackbar(text=text, y=dp(24)).open()

    def _go_back(self):
        self.manager.current = "driver_home"
