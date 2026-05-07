# ============================================================
# Écran Wallet Chauffeur
# Fichier : mobile/screens/driver/wallet_screen.py
# Description : Gestion du wallet et des revenus
# ============================================================

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.graphics import Color, RoundedRectangle
from mobile.theme.colors import Colors


class WalletScreen(Screen):
    """Écran wallet MobiTranz pour chauffeurs."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()
    
    def build_ui(self):
        """Construction de l'interface."""
        layout = BoxLayout(orientation="vertical", padding=20, spacing=15)
        
        layout.add_widget(Label(
            text="Mon Wallet",
            font_size=28,
            size_hint_y=None,
            height=50,
            color=Colors.TEXT_PRIMARY
        ))
        
        scroll = ScrollView()
        content = BoxLayout(orientation="vertical", padding=10, spacing=15, size_hint_y=None)
        content.bind(minimum_height=content.setter('height'))
        
        content.add_widget(self._create_balance_card())
        content.add_widget(self._create_recent_transactions())
        
        scroll.add_widget(content)
        layout.add_widget(scroll)
        
        self.add_widget(layout)
    
    def _create_balance_card(self):
        """Crée la carte de solde."""
        card = BoxLayout(
            orientation="vertical",
            padding=20,
            spacing=10,
            size_hint_y=None,
            height="180dp"
        )
        
        with card.canvas.before:
            Color(rgba=Colors.ACCENT)
            card._bg = RoundedRectangle(
                pos=card.pos, size=card.size, radius=[16, 16, 16, 16]
            )
        
        card.bind(pos=self._update_bg, size=self._update_bg)
        
        card.add_widget(Label(
            text="Solde disponible",
            font_size=14,
            color=(1, 1, 1, 0.7)
        ))
        
        card.add_widget(Label(
            text="15,750 XAF",
            font_size=36,
            color=(1, 1, 1, 1)
        ))
        
        card.add_widget(Label(
            text="En attente: 2,500 XAF",
            font_size=12,
            color=(1, 1, 1, 0.6)
        ))
        
        return card
    
    def _update_bg(self, instance, value):
        """Met à jour le fond."""
        instance.canvas.before.ask_update()
    
    def _create_recent_transactions(self):
        """Crée la liste des transactions récentes."""
        container = BoxLayout(orientation="vertical", size_hint_y=None, height="300dp")
        
        container.add_widget(Label(
            text="Transactions récentes",
            font_size=18,
            size_hint_y=None,
            height=40,
            color=Colors.TEXT_PRIMARY
        ))
        
        transactions = [
            {"type": "Trip", "amount": "+1,500 XAF", "date": "Aujourd'hui, 14:30"},
            {"type": "Trip", "amount": "+2,000 XAF", "date": "Aujourd'hui, 10:15"},
            {"type": "Retrait", "amount": "-10,000 XAF", "date": "Hier, 16:00"},
            {"type": "Trip", "amount": "+800 XAF", "date": "Hier, 09:45"},
        ]
        
        for txn in transactions:
            container.add_widget(self._create_transaction_item(txn))
        
        return container
    
    def _create_transaction_item(self, txn):
        """Crée un élément de transaction."""
        item = BoxLayout(
            size_hint_y=None,
            height=60,
            padding=10,
            spacing=10
        )
        
        item.add_widget(Label(
            text=txn["type"],
            size_hint_x=0.3,
            color=Colors.TEXT_SECONDARY
        ))
        
        amount_color = (0, 0.8, 0, 1) if "+" in txn["amount"] else (0.8, 0, 0, 1)
        item.add_widget(Label(
            text=txn["amount"],
            size_hint_x=0.4,
            color=amount_color
        ))
        
        item.add_widget(Label(
            text=txn["date"],
            size_hint_x=0.3,
            color=Colors.TEXT_SECONDARY,
            font_size=12
        ))
        
        return item