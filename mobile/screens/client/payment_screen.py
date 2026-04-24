# ============================================================
# Écran Paiement Mobile
# Fichier : mobile/screens/client/payment_screen.py
# ============================================================

from kivy.uix.screen import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from mobile.theme.colors import Colors


class PaymentScreen(Screen):
    """Écran de paiement."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "payment"
        self._build_ui()
    
    def _build_ui(self):
        layout = BoxLayout(orientation="vertical", padding=20, spacing=16)
        
        # Header
        header = BoxLayout(size_hint_y=None, height=60)
        back_btn = Button(text="←", size_hint_x=0.15, background_color=Colors.SURFACE,
                       on_press=lambda x: setattr(self.manager, 'current', 'home'))
        title = Label(text="💳 Paiement", font_size=20, color=Colors.PRIMARY, size_hint_x=0.7)
        header.add_widget(back_btn)
        header.add_widget(title)
        layout.add_widget(header)
        
        # Trip summary
        trip_card = BoxLayout(orientation="vertical", padding=16, background_color=Colors.PRIMARY, radius=[12])
        trip_card.add_widget(Label(text="Trajet vers Owendo", font_size=16, color=(1,1,1,1)))
        trip_card.add_widget(Label(text="1,000 XAF", font_size=24, color=(1,1,1,1)))
        trip_card.add_widget(Label(text="2 places", font_size=14, color=(1,1,1,0.7)))
        layout.add_widget(trip_card)
        
        # Payment methods
        layout.add_widget(Label(text="Choisir le mode de paiement", font_size=14, color=Colors.TEXT_SECONDARY))
        
        methods = [
            ("📱 MoovMoney", Colors.PRIMARY),
            ("📱 Airtel Money", Colors.ACCENT),
            ("💳 Carte bancaire", Colors.WARNING),
            ("👆 Empreinte", Colors.DANGER),
        ]
        
        for text, color in methods:
            btn = Button(text=text, height=56, background_color=Colors.SURFACE, color=Colors.TEXT_PRIMARY)
            btn.bind(on_press=lambda x, m=text: self.select_method(m))
            layout.add_widget(btn)
        
        # Phone input
        phone_input = BoxLayout(size_hint_y=None, height=50)
        phone_input.add_widget(Label(text="Numéro:", width=100, color=Colors.TEXT_SECONDARY))
        self.phone_field = TextInput(hint_text="+241 XX XX XX XX", multiline=False)
        phone_input.add_widget(self.phone_field)
        layout.add_widget(phone_input)
        
        # Pay button
        pay_btn = Button(text="Payer 1,000 XAF", height=56, background_color=Colors.ACCENT, color=(1,1,1,1))
        pay_btn.bind(on_press=self.process_payment)
        layout.add_widget(pay_btn)
        
        self.add_widget(layout)
    
    def select_method(self, method):
        """Sélectionne une méthode de paiement."""
        print(f"Méthode sélectionnée: {method}")
    
    def process_payment(self, instance):
        """Traitement du paiement."""
        self.manager.current = "trip_active"