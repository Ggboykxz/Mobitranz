# ============================================================
# Écran Porte-Monnaie Driver
# Fichier : mobile/screens/driver/wallet_screen.py
# Description : Solde + retrait MoovMoney/Airtel
# ============================================================

from kivy.uix.screen import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from mobile.theme.colors import Colors


class WalletScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "wallet"
        self._balance = 15750
        self._pending = 2500
        
        layout = BoxLayout(orientation="vertical", padding=20, spacing=15)
        
        header = BoxLayout(
            size_hint_y=None,
            height="56dp",
            padding=10,
            background_color=Colors.ACCENT
        )
        header.add_widget(Label(
            text="Porte-Monnaie",
            font_size=20,
            color=(1, 1, 1, 1)
        ))
        
        card = BoxLayout(
            orientation="vertical",
            padding=20,
            spacing=10,
            size_hint_y=None,
            height="180dp",
            canvas.before={
                "Color": {"rgba": Colors.ACCENT},
                "RoundedRectangle": {
                    "pos": self.pos, "size": self.size,
                    "radius": [16, 16, 16, 16]
                }
            }
        )
        
        card.add_widget(Label(
            text="Solde disponible",
            font_size=14,
            color=(1, 1, 1, 0.7)
        ))
        
        card.add_widget(Label(
            text="15,750 XAF",
            font_size=36,
            color=(1, 1, 1, 1),
            font_name="Roboto-Bold"
        ))
        
        card.add_widget(Label(
            text="En attente: 2,500 XAF",
            font_size=12,
            color=(1, 1, 1, 0.6)
        ))
        
        actions = BoxLayout(size_hint_y=None, height="50dp", spacing=10)
        
        withdraw_btn = Button(
            text="Retirer",
            background_color=(1, 1, 1, 0.2),
            color=(1, 1, 1, 1),
            on_press=self.show_withdraw
        )
        
        topup_btn = Button(
            text="Recharger",
            background_color=(1, 1, 1, 0.2),
            color=(1, 1, 1, 1),
            on_press=lambda x: None
        )
        
        actions.add_widget(withdraw_btn)
        actions.add_widget(topup_btn)
        
        history_title = Label(
            text="Historique",
            font_size=16,
            color=Colors.TEXT_PRIMARY,
            size_hint_y=None,
            height="36dp",
            halign="left"
        )
        
        history_scroll = BoxLayout(
            orientation="vertical",
            size_hint_y=0.5,
            spacing=1
        )
        
        sample_txs = [
            ("+2,000 XAF", "MoovMoney", True, "10:30"),
            ("+1,500 XAF", "Airtel Money", True, "09:15"),
            ("-500 XAF", "Retrait", False, "Hier"),
            ("+3,000 XAF", "MoovMoney", True, "Hier"),
        ]
        
        for amount, method, is_credit, time in sample_txs:
            tx_row = BoxLayout(
                size_hint_y=None,
                height="50dp",
                padding=5
            )
            
            icon = "+" if is_credit else "-"
            color = Colors.ACCENT if is_credit else Colors.TEXT_SECONDARY
            
            tx_row.add_widget(Label(
                text=amount,
                font_size=14,
                color=color,
                size_hint_x=0.35
            ))
            tx_row.add_widget(Label(
                text=method,
                font_size=12,
                color=Colors.TEXT_SECONDARY,
                size_hint_x=0.4
            ))
            tx_row.add_widget(Label(
                text=time,
                font_size=12,
                color=Colors.TEXT_SECONDARY,
                size_hint_x=0.25
            ))
            
            history_scroll.add_widget(tx_row)
        
        layout.add_widget(header)
        layout.add_widget(card)
        layout.add_widget(actions)
        layout.add_widget(history_title)
        layout.add_widget(history_scroll)
        
        self.add_widget(layout)
    
    def show_withdraw(self, instance):
        popup_layout = BoxLayout(
            orientation="vertical",
            padding=20,
            spacing=15,
            size=(300, 250)
        )
        
        popup_layout.add_widget(Label(
            text="Retirer de l'argent",
            font_size=18,
            color=Colors.PRIMARY,
            size_hint_y=None,
            height="36dp"
        ))
        
        self.withdraw_input = TextInput(
            hint_text="Montant XAF",
            multiline=False,
            input_type="number",
            size_hint_y=None,
            height="48dp"
        )
        
        method_layout = BoxLayout(size_hint_y=None, height="36dp", spacing=10)
        method_layout.add_widget(Button(
            text="MoovMoney",
            on_press=lambda x: setattr(self, "_selected_method", "moovmoney")
        ))
        method_layout.add_widget(Button(
            text="Airtel Money",
            on_press=lambda x: setattr(self, "_selected_method", "airtelmoney")
        ))
        
        confirm_btn = Button(
            text="Confirmer",
            background_color=Colors.ACCENT,
            color=(1, 1, 1, 1),
            size_hint_y=None,
            height="48dp",
            on_press=self.process_withdraw
        )
        
        popup_layout.add_widget(self.withdraw_input)
        popup_layout.add_widget(method_layout)
        popup_layout.add_widget(confirm_btn)
        
        self._popup = Popup(
            title="",
            content=popup_layout,
            size_hint=(0.8, 0.4),
            auto_dismiss=True
        )
        self._popup.open()
    
    def process_withdraw(self, instance):
        amount_text = self.withdraw_input.text.strip()
        if amount_text and amount_text.isdigit():
            amount = int(amount_text)
            if amount > 0 and amount <= self._balance:
                self._popup.dismiss()
        self._popup.dismiss()