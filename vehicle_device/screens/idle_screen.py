# ============================================================
# Écran d'Attente Véhicule
# Fichier : vehicle_device/screens/idle_screen.py
# Description : Écran attente (revenus du jour, connexion)
# ============================================================

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen


class IdleScreen(Screen):
    """Écran d'attente de l'interface véhicule.

    Affiche les revenus du jour et le statut de connexion.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "idle"
        self._build_ui()

    def _build_ui(self):
        layout = BoxLayout(orientation="vertical", padding=40, spacing=20)

        title = Label(
            text="MobiTranz Véhicule",
            font_size=24,
            size_hint_y=None,
            height=50
        )
        layout.add_widget(title)

        status_frame = BoxLayout(orientation="vertical", padding=20, size_hint_y=None, height=100)
        status_frame.add_widget(Label(text="Statut", font_size=16))
        self.status_label = Label(text="En attente", font_size=18)
        status_frame.add_widget(self.status_label)
        layout.add_widget(status_frame)

        stats_frame = BoxLayout(orientation="vertical", padding=20, size_hint_y=None, height=150)
        stats_frame.add_widget(Label(text="Revenus du jour", font_size=16))
        self.revenue_label = Label(text="0 XAF", font_size=32)
        stats_frame.add_widget(self.revenue_label)
        layout.add_widget(stats_frame)

        self.add_widget(layout)

    def update_status(self, status: str):
        """Met à jour le statut."""
        self.status_label.text = status

    def update_revenue(self, revenue: int):
        """Met à jour les revenus."""
        self.revenue_label.text = f"{revenue} XAF"