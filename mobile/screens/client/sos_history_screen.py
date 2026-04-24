# ============================================================
# Écran Historique SOS
# Fichier : mobile/screens/client/sos_history_screen.py
# Description : Liste des incidents signalés
# ============================================================

from kivy.uix.screen import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.label import Label
from mobile.theme.colors import Colors


STATUS_COLORS = {
    "pending": Colors.WARNING,
    "acknowledged": Colors.PRIMARY,
    "resolved": Colors.ACCENT,
    "escalated": Colors.DANGER,
}


class SOSHistoryScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "sos_history"
        
        layout = BoxLayout(orientation="vertical", padding=0, spacing=0)
        
        header = BoxLayout(
            size_hint_y=None,
            height="56dp",
            padding=10,
            background_color=Colors.DANGER
        )
        header.add_widget(Label(
            text="Historique SOS",
            font_size=20,
            color=(1, 1, 1, 1)
        ))
        
        scroll = ScrollView(size_hint=(1, 1), do_scroll_x=False)
        list_layout = BoxLayout(
            orientation="vertical",
            padding=0,
            spacing=1,
            size_hint_y=None,
            height="0dp"
        )
        scroll.add_widget(list_layout)
        
        layout.add_widget(header)
        layout.add_widget(scroll)
        
        self.add_widget(layout)
        
        self._load_incidents(list_layout)
    
    def _load_incidents(self, list_layout):
        list_layout.clear_widgets()
        total = 0
        
        sample_incidents = [
            {
                "type": "Accident",
                "location": "PK5, Libreville",
                "status": "resolved",
                "date": "15 Avr 2026",
                "description": "Collision mineure, pas de blessé"
            },
            {
                "type": "Comportement",
                "location": "Centre-ville",
                "status": "acknowledged",
                "date": "10 Avr 2026",
                "description": "Conducteur verbalement agressif"
            },
            {
                "type": "Arnaque",
                "location": "Owendo",
                "status": "escalated",
                "date": "02 Avr 2026",
                "description": "Tentative de surcoût"
            },
        ]
        
        for inc in sample_incidents:
            item = self._build_incident_card(inc)
            list_layout.add_widget(item)
            total += 90
        
        list_layout.height = total + 10
    
    def _build_incident_card(self, inc: dict) -> BoxLayout:
        status_color = STATUS_COLORS.get(inc["status"], Colors.TEXT_SECONDARY)
        status_labels = {
            "pending": "En attente",
            "acknowledged": "Pris en charge",
            "resolved": "Résolu",
            "escalated": "Escaladé",
        }
        
        card = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            height="80dp",
            padding=12,
            spacing=5
        )
        
        row1 = BoxLayout(size_hint_y=None, height="24dp")
        row1.add_widget(Label(
            text=f"🆘 {inc['type']}",
            font_size=14,
            color=Colors.TEXT_PRIMARY,
            size_hint_x=1,
            halign="left"
        ))
        row1.add_widget(Label(
            text=status_labels.get(inc["status"], ""),
            font_size=12,
            color=status_color,
            size_hint_x=None,
            width="90dp"
        ))
        
        row2 = BoxLayout(size_hint_y=None, height="20dp")
        row2.add_widget(Label(
            text=f"📍 {inc['location']}",
            font_size=12,
            color=Colors.TEXT_SECONDARY
        ))
        row2.add_widget(Label(
            text=inc["date"],
            font_size=12,
            color=Colors.TEXT_SECONDARY,
            size_hint_x=None,
            width="90dp"
        ))
        
        desc = Label(
            text=inc.get("description", ""),
            font_size=11,
            color=Colors.TEXT_SECONDARY,
            size_hint_y=1,
            text_size=(300, None),
            halign="left",
            valign="top"
        )
        
        card.add_widget(row1)
        card.add_widget(row2)
        card.add_widget(desc)
        
        return card