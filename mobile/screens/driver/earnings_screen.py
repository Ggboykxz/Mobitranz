# ============================================================
# Écran Revenus Taximan
# Fichier : mobile/screens/driver/earnings_screen.py
# ============================================================

from kivy.uix.screen import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from mobile.theme.colors import Colors


class EarningsScreen(Screen):
    """Écran des revenus et statistiques taximan."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "earnings"
        self._build_ui()
    
    def _build_ui(self):
        layout = BoxLayout(orientation="vertical", padding=20, spacing=16)
        
        # Header
        header = BoxLayout(size_hint_y=None, height=60)
        back_btn = Button(text="←", size_hint_x=0.15, background_color=Colors.SURFACE,
                       on_press=lambda x: setattr(self.manager, 'current', 'driver_home'))
        title = Label(text="💰 Revenus", font_size=20, color=Colors.PRIMARY, size_hint_x=0.7)
        header.add_widget(back_btn)
        header.add_widget(title)
        layout.add_widget(header)
        
        # Total today
        total = BoxLayout(orientation="vertical", padding=20, background_color=Colors.PRIMARY, radius=[12])
        total.add_widget(Label(text="AUJOURD'HUI", font_size=12, color=(1,1,1,0.7)))
        total.add_widget(Label(text="12,500 XAF", font_size=32, color=(1,1,1,1)))
        layout.add_widget(total)
        
        # Stats
        stats = BoxLayout(size_hint_y=None, height=100, spacing=12)
        for label, value in [("Cette semaine", "89,500"), ("Ce mois", "445,000"), ("Note", "⭐4.9")]:
            col = BoxLayout(orientation="vertical", background_color=Colors.SURFACE, radius=[8])
            col.add_widget(Label(text=str(value), font_size=18, color=Colors.PRIMARY, bold=True))
            col.add_widget(Label(text=label, font_size=12, color=Colors.TEXT_SECONDARY))
            stats.add_widget(col)
        layout.add_widget(stats)
        
        # History
        layout.add_widget(Label(text="Historique", font_size=14, color=Colors.TEXT_SECONDARY))
        
        for date, amount in [("Mardi", "18,500"), ("Lundi", "15,200"), ("Dimanche", "22,800")]:
            row = BoxLayout(size_hint_y=None, height=50, background_color=Colors.SURFACE, radius=[8])
            row.add_widget(Label(text=date, size_hint_x=0.5, color=Colors.TEXT_PRIMARY))
            row.add_widget(Label(text=f"{amount} XAF", size_hint_x=0.5, color=Colors.PRIMARY))
            layout.add_widget(row)
        
        # Withdraw
        withdraw_btn = Button(text="💳 Retirer mes gains", height=56, background_color=Colors.ACCENT, color=(1,1,1,1))
        layout.add_widget(withdraw_btn)
        
        self.add_widget(layout)