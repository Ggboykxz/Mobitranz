# ============================================================
# Écran Accueil Taximan
# Fichier : mobile/screens/driver/driver_home_screen.py
# ============================================================

from kivy.uix.screen import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from mobile.theme.colors import Colors


class DriverHomeScreen(Screen):
    """Écran d'accueil taximan."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "driver_home"
        self._is_available = False
        self._build_ui()
    
    def _build_ui(self):
        layout = BoxLayout(orientation="vertical", padding=20, spacing=16)
        
        # Header
        header = BoxLayout(size_hint_y=None, height=60)
        title = Label(text="🚕 MobiTranz", font_size=20, color=Colors.PRIMARY, size_hint_x=0.7)
        profile_btn = Label(text="👤", font_size=24, size_hint_x=0.3)
        header.add_widget(title)
        header.add_widget(profile_btn)
        layout.add_widget(header)
        
        # Status toggle
        self.status_btn = Button(
            text="● Disponible",
            height=60,
            background_color=Colors.GREY_400,
            color=(1,1,1,1),
            on_press=self.toggle_status
        )
        layout.add_widget(self.status_btn)
        
        # Stats today
        stats = BoxLayout(size_hint_y=None, height=100, spacing=12)
        for label, value in [("Trajets", "8"), ("Revenus", "12,500"), ("_note", "⭐4.9")]:
            col = BoxLayout(orientation="vertical", background_color=Colors.SURFACE, radius=[8])
            col.add_widget(Label(text=str(value), font_size=20, color=Colors.PRIMARY, bold=True))
            col.add_widget(Label(text=label, font_size=12, color=Colors.TEXT_SECONDARY))
            stats.add_widget(col)
        layout.add_widget(stats)
        
        # Recent proposal
        proposal_section = Label(text="DERNIÈRE PROPOSITION", font_size=12, color=Colors.TEXT_SECONDARY)
        layout.add_widget(proposal_section)
        
        self.proposal = BoxLayout(orientation="vertical", padding=16, background_color=Colors.SURFACE, radius=[12])
        self.proposal.add_widget(Label(text="→ Centre-ville", font_size=16, color=Colors.PRIMARY))
        self.proposal.add_widget(Label(text="1,500 XAF · 2 places", font_size=14, color=Colors.TEXT_SECONDARY))
        self.proposal.add_widget(Label(text="Client: Marie (+241...)", font_size=12, color=Colors.TEXT_SECONDARY))
        
        proposal_btns = BoxLayout(size_hint_y=None, height=50, spacing=8)
        accept_btn = Button(text="✓ Accepter", background_color=Colors.ACCENT, color=(1,1,1,1))
        reject_btn = Button(text="✗ Refuser", background_color=Colors.DANGER, color=(1,1,1,1))
        proposal_btns.add_widget(accept_btn)
        proposal_btns.add_widget(reject_btn)
        self.proposal.add_widget(proposal_btns)
        
        layout.add_widget(self.proposal)
        
        self.add_widget(layout)
    
    def toggle_status(self, instance):
        """Bascule le statut disponibilidad."""
        self._is_available = not self._is_available
        if self._is_available:
            self.status_btn.text = "● En service"
            self.status_btn.background_color = Colors.ACCENT
        else:
            self.status_btn.text = "● Hors service"
            self.status_btn.background_color = Colors.GREY_400