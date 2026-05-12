from kivy.clock import Clock
from kivy.metrics import dp
from kivy.properties import NumericProperty, BooleanProperty
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


class WalletScreen(MDScreen):
    _loading = BooleanProperty(True)
    _balance = NumericProperty(0)
    _pending = NumericProperty(0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "wallet"
        self._build_ui()

    def _build_ui(self):
        layout = MDBoxLayout(orientation="vertical", spacing=dp(8))

        layout.add_widget(MDTopAppBar(
            title="Mon Wallet",
            left_action_items=[["arrow-left", lambda x: self._go_back()]],
            right_action_items=[["refresh", lambda x: self._refresh()]],
            elevation=2
        ))

        scroll = MDScrollView()
        content = MDBoxLayout(
            orientation="vertical",
            spacing=dp(16),
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

        self.balance_card = MDCard(
            orientation="vertical",
            size_hint_y=None,
            height=dp(160),
            padding=dp(24),
            spacing=dp(12),
            radius=[dp(20)],
            elevation=4
        )
        self.balance_card.md_bg_color = Colors.ACCENT_BG
        self.balance_card.add_widget(MDLabel(
            text="Solde disponible",
            font_style="Subtitle1",
            halign="center",
            theme_text_color="Custom",
            text_color=[1, 1, 1, 0.7],
            adaptive_height=True
        ))
        self.balance_amount = MDLabel(
            text="0 XAF",
            font_style="H2",
            halign="center",
            theme_text_color="Custom",
            text_color=[1, 1, 1, 1],
            adaptive_height=True
        )
        self.balance_card.add_widget(self.balance_amount)
        self.pending_label = MDLabel(
            text="En attente: 0 XAF",
            font_style="Caption",
            halign="center",
            theme_text_color="Custom",
            text_color=[1, 1, 1, 0.6],
            adaptive_height=True
        )
        self.balance_card.add_widget(self.pending_label)
        content.add_widget(self.balance_card)

        self.empty_state = MDBoxLayout(
            orientation="vertical",
            size_hint_y=None,
            height=dp(120),
            spacing=dp(8)
        )
        self.empty_state.add_widget(MDLabel(
            text="wallet-outline",
            font_style="H1",
            halign="center",
            adaptive_height=True,
            theme_text_color="Secondary"
        ))
        self.empty_state.add_widget(MDLabel(
            text="Aucune transaction",
            font_style="Subtitle1",
            halign="center",
            adaptive_height=True,
            theme_text_color="Secondary"
        ))
        self.empty_state.add_widget(MDLabel(
            text="Vos transactions apparaitront ici",
            font_style="Caption",
            halign="center",
            adaptive_height=True,
            theme_text_color="Secondary"
        ))
        content.add_widget(self.empty_state)
        self.empty_state.opacity = 0

        content.add_widget(MDLabel(
            text="Transactions recentes",
            font_style="Subtitle1",
            theme_text_color="Primary",
            adaptive_height=True
        ))

        self.transaction_container = MDBoxLayout(
            orientation="vertical",
            spacing=dp(6),
            adaptive_height=True
        )
        content.add_widget(self.transaction_container)

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
        asyncio.ensure_future(self._fetch_wallet())

    async def _fetch_wallet(self):
        try:
            wallet_data = await api_client.get("/api/v1/wallet")
            txn_data = await api_client.get("/api/v1/wallet/transactions")
            Clock.schedule_once(lambda dt: self._update_wallet(wallet_data, txn_data))
        except Exception as e:
            Clock.schedule_once(lambda dt: self._show_error(str(e)))

    def _update_wallet(self, wallet_data, txn_data):
        self._loading = False
        self.spinner.active = False

        balance = wallet_data.get("balance", wallet_data.get("amount", 0))
        pending = wallet_data.get("pending", wallet_data.get("pending_amount", 0))
        self._balance = balance
        self._pending = pending

        self.balance_amount.text = f"{balance:,} XAF" if isinstance(balance, (int, float)) else str(balance)
        self.pending_label.text = f"En attente: {pending:,} XAF" if isinstance(pending, (int, float)) else f"En attente: {str(pending)} XAF"

        transactions = txn_data if isinstance(txn_data, list) else txn_data.get("transactions", [])
        self.transaction_container.clear_widgets()

        if not transactions:
            self.empty_state.opacity = 1
            return

        self.empty_state.opacity = 0
        for txn in transactions:
            txn_type = txn.get("type", txn.get("description", "Transaction"))
            amount = txn.get("amount", 0)
            date = txn.get("date", txn.get("created_at", ""))

            sign = "+" if (isinstance(amount, (int, float)) and amount >= 0) else ""
            amount_str = f"{sign}{amount:,} XAF" if isinstance(amount, (int, float)) else str(amount)
            is_positive = isinstance(amount, (int, float)) and amount >= 0

            txn_card = MDCard(
                orientation="vertical",
                size_hint_y=None,
                height=dp(64),
                padding=[dp(12), dp(8)],
                spacing=dp(4),
                radius=[dp(8)],
                elevation=1
            )
            top_row = MDBoxLayout(adaptive_height=True, spacing=dp(8))
            top_row.add_widget(MDLabel(
                text=txn_type,
                font_style="Body1",
                adaptive_height=True,
                theme_text_color="Primary",
                size_hint_x=0.6
            ))
            top_row.add_widget(MDLabel(
                text=amount_str,
                font_style="Subtitle2",
                adaptive_height=True,
                theme_text_color="Custom",
                text_color=Colors.ACCENT if is_positive else Colors.DANGER,
                size_hint_x=0.4,
                halign="right"
            ))
            txn_card.add_widget(top_row)
            txn_card.add_widget(MDLabel(
                text=date if isinstance(date, str) else str(date),
                font_style="Caption",
                adaptive_height=True,
                theme_text_color="Secondary"
            ))
            self.transaction_container.add_widget(txn_card)

    def _show_error(self, message):
        self._loading = False
        self.spinner.active = False
        self._show_snackbar(f"Erreur: {message}")

    def _show_snackbar(self, text):
        MDSnackbar(text=text, y=dp(24)).open()

    def _go_back(self):
        self.manager.current = "driver_home"
