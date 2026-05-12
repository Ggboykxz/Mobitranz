from kivy.clock import Clock
from kivy.uix.screenmanager import Screen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton, MDFlatButton, MDIconButton
from kivymd.uix.spinner import MDSpinner
from kivymd.uix.snackbar import MDSnackbar
from kivymd.uix.topappbar import MDTopAppBar
from kivymd.uix.textfield import MDTextField
from kivymd.uix.dialog import MDDialog
from kivy.metrics import dp
from mobile.services.api_client import api_client


class PaymentScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "payment"
        self.trip_id = None
        self.trip_info = {}
        self.selected_method = None
        self._dialog = None
        self._build_ui()

    def _build_ui(self):
        self.root = MDBoxLayout(orientation="vertical", md_bg_color="#F7F9FC")

        self.top_bar = MDTopAppBar(
            title="Paiement",
            md_bg_color="#1A3A6C",
            specific_text_color="#FFFFFF",
            left_action_items=[["arrow-left", lambda x: self.go_back()]],
        )
        self.root.add_widget(self.top_bar)

        body = MDBoxLayout(orientation="vertical", padding=[20, 16], spacing=16)

        self.trip_card = MDCard(
            orientation="vertical",
            size_hint_y=None,
            height=dp(120),
            padding=16,
            spacing=8,
            md_bg_color="#1A3A6C",
            radius=[12],
        )
        self.trip_dest_label = MDLabel(
            text="Destination: --",
            font_style="Subtitle1",
            theme_text_color="Custom",
            text_color="#FFFFFF",
        )
        self.trip_amount_label = MDLabel(
            text="Montant: -- XAF",
            font_style="H5",
            theme_text_color="Custom",
            text_color="#FFFFFF",
            bold=True,
        )
        self.trip_seats_label = MDLabel(
            text="Places: --",
            font_style="Body2",
            theme_text_color="Custom",
            text_color="#FFFFFF",
            opacity=0.7,
        )
        self.trip_card.add_widget(self.trip_dest_label)
        self.trip_card.add_widget(self.trip_amount_label)
        self.trip_card.add_widget(self.trip_seats_label)
        body.add_widget(self.trip_card)

        body.add_widget(
            MDLabel(
                text="Choisir le mode de paiement",
                font_style="Subtitle2",
                theme_text_color="Secondary",
                size_hint_y=None,
                height=dp(30),
            )
        )

        self.methods_container = MDBoxLayout(
            orientation="vertical",
            spacing=8,
            size_hint_y=None,
            height=dp(220),
        )

        payment_methods = [
            ("bank-transfer", "Moov Money", "#1A3A6C"),
            ("phone", "Airtel Money", "#009E60"),
            ("credit-card", "Carte bancaire", "#FCD116"),
            ("fingerprint", "Empreinte", "#E53E3E"),
        ]

        self.method_buttons = {}
        for icon, name, color in payment_methods:
            card = MDCard(
                orientation="horizontal",
                size_hint_y=None,
                height=dp(48),
                padding=[12, 8],
                spacing=12,
                md_bg_color="#FFFFFF",
                radius=[8],
                ripple_behavior=True,
            )
            icon_btn = MDIconButton(icon=icon, icon_color=color, theme_icon_size="Custom", icon_size=dp(24))
            label = MDLabel(
                text=name,
                font_style="Body1",
                theme_text_color="Primary",
                halign="left",
            )
            card.add_widget(icon_btn)
            card.add_widget(label)
            card.bind(on_release=lambda x, m=name: self.select_method(m))
            self.method_buttons[name] = card
            self.methods_container.add_widget(card)

        body.add_widget(self.methods_container)

        self.phone_field = MDTextField(
            hint_text="+241 XX XX XX XX",
            helper_text="Numero pour le paiement mobile",
            mode="round",
            size_hint_y=None,
            height=dp(50),
        )
        body.add_widget(self.phone_field)

        self.pay_btn = MDRaisedButton(
            text="Payer",
            md_bg_color="#009E60",
            text_color="#FFFFFF",
            size_hint=(1, None),
            height=dp(52),
            on_release=self.process_payment,
            disabled=True,
        )
        body.add_widget(self.pay_btn)

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
        Clock.schedule_once(lambda dt: self.load_trip_data())

    def load_trip_data(self):
        self.trip_id = getattr(self, "trip_id", None) or getattr(self.manager, "current_trip_id", None)
        if self.trip_id:
            Clock.schedule_once(lambda dt: self.fetch_trip_details())

    async def fetch_trip_details(self):
        self.spinner.active = True
        try:
            data = await api_client.get(f"/api/v1/trips/{self.trip_id}")
            self.trip_info = data
            Clock.schedule_once(lambda dt: self.update_trip_card(data))
        except Exception:
            MDSnackbar(text="Impossible de charger les details du trajet", snackbar_x=10, snackbar_y=10).open()
        finally:
            Clock.schedule_once(lambda dt: setattr(self.spinner, "active", False))

    def update_trip_card(self, data):
        dest = data.get("destination", "--")
        amount = data.get("estimated_price", data.get("price", "--"))
        seats = data.get("seats", data.get("passengers", "--"))
        self.trip_dest_label.text = f"Destination: {dest}"
        self.trip_amount_label.text = f"Montant: {amount} XAF"
        self.trip_seats_label.text = f"Places: {seats}"

    def select_method(self, method_name):
        self.selected_method = method_name
        for name, card in self.method_buttons.items():
            card.md_bg_color = "#E8F0FE" if name == method_name else "#FFFFFF"
        self.pay_btn.disabled = False
        MDSnackbar(text=f"Methode selectionnee: {method_name}", snackbar_x=10, snackbar_y=10).open()

    def process_payment(self, instance):
        if not self.selected_method:
            MDSnackbar(text="Veuillez selectionner un moyen de paiement", snackbar_x=10, snackbar_y=10).open()
            return
        phone = self.phone_field.text.strip()
        if not phone:
            MDSnackbar(text="Veuillez entrer un numero de telephone", snackbar_x=10, snackbar_y=10).open()
            return
        Clock.schedule_once(lambda dt: self.initiate_payment(phone))

    async def initiate_payment(self, phone):
        self.spinner.active = True
        self.pay_btn.disabled = True
        try:
            result = await api_client.start_payment(
                trip_id=self.trip_id or "unknown",
                method=self.selected_method,
                phone=phone,
            )
            status = result.get("status", "pending")
            MDSnackbar(
                text=f"Paiement {status}. Redirection en cours...",
                snackbar_x=10,
                snackbar_y=10,
            ).open()
            Clock.schedule_once(lambda dt: self.go_to_active_trip(), 1)
        except Exception as e:
            MDSnackbar(text=f"Erreur de paiement: {str(e)}", snackbar_x=10, snackbar_y=10).open()
        finally:
            self.spinner.active = False
            self.pay_btn.disabled = False

    def go_to_active_trip(self):
        self.manager.current = "trip_active"
