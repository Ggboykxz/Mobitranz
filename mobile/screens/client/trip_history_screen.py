# ============================================================
# Écran Historique Trajets
# Fichier : mobile/screens/client/trip_history_screen.py
# ============================================================

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from mobile.theme.colors import Colors


class TripHistoryScreen(Screen):
    """Écran d'historique des trajets."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "trip_history"
        self._build_ui()
    
    def _build_ui(self):
        layout = BoxLayout(orientation="vertical", padding=20, spacing=12)
        
        # Header
        header = BoxLayout(size_hint_y=None, height=60)
        back_btn = Button(text="←", size_hint_x=0.15, background_color=Colors.SURFACE,
                       on_press=lambda x: setattr(self.manager, 'current', 'home'))
        title = Label(text="📋 Historique", font_size=20, color=Colors.PRIMARY, size_hint_x=0.7)
        header.add_widget(back_btn)
        header.add_widget(title)
        layout.add_widget(header)
        
        # Filter tabs
        tabs = BoxLayout(size_hint_y=None, height=40)
        for tab in ["Tout", "Ce jour", "Cette semaine", "Ce mois"]:
            btn = Button(text=tab, size_hint_x=0.25, background_color=Colors.SURFACE, color=Colors.TEXT_PRIMARY, font_size=11)
            tabs.add_widget(btn)
        layout.add_widget(tabs)
        
        # Trip list
        trips = [
            ("14:32", "Owendo → Centre-ville", "1,500 XAF", "✅ Terminé"),
            ("10:15", "Akanda → Owendo", "800 XAF", "✅ Terminé"),
            ("Hier 18:00", "Libreville → Port-Gentil", "5,000 XAF", "✅ Terminé"),
        ]
        
        for time, route, amount, status in trips:
            trip_card = BoxLayout(orientation="vertical", padding=12, background_color=Colors.SURFACE, radius=[8])
            top = BoxLayout(size_hint_y=None, height=30)
            top.add_widget(Label(text=time, font_size=12, color=Colors.TEXT_SECONDARY, size_hint_x=0.2))
            top.add_widget(Label(text=status, font_size=12, color=Colors.ACCENT if "✅" in status else Colors.DANGER, size_hint_x=0.8))
            trip_card.add_widget(top)
            trip_card.add_widget(Label(text=route, font_size=14, color=Colors.TEXT_PRIMARY))
            trip_card.add_widget(Label(text=amount, font_size=16, color=Colors.PRIMARY, weight="bold"))
            layout.add_widget(trip_card)
        
        # Summary
        summary = BoxLayout(size_hint_y=None, height=80, background_color=Colors.GREY_100, radius=[12])
        summary.add_widget(Label(text="Total: 3 trajets\n7,300 XAF", font_size=14, color=Colors.TEXT_PRIMARY))
        layout.add_widget(summary)
        
        self.add_widget(layout)