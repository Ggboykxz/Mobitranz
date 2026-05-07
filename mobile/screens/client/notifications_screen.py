# ============================================================
# Écran Notifications
# Fichier : mobile/screens/client/notifications_screen.py
# Description : Liste des notifications push
# ============================================================

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.storage.jsonstore import JsonStore
from mobile.theme.colors import Colors


NOTIF_ICONS = {
    "trip": "🚕",
    "payment": "💳",
    "driver": "👤",
    "sos": "🆘",
    "system": "ℹ️",
}


class NotifItem(BoxLayout):
    def __init__(self, notif: dict, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "horizontal"
        self.size_hint_y = None
        self.height = "70dp"
        self.padding = 10
        self.spacing = 10
        
        icon = NOTIF_ICONS.get(notif.get("type", "system"), "ℹ️")
        is_read = notif.get("is_read", False)
        
        icon_label = Label(
            text=icon,
            font_size=24,
            size_hint_x=None,
            width="40dp",
            color=Colors.TEXT_PRIMARY if is_read else Colors.PRIMARY
        )
        
        content = BoxLayout(orientation="vertical", size_hint_x=1)
        title_label = Label(
            text=notif.get("title", "Notification"),
            font_size=14,
            color=Colors.TEXT_PRIMARY if is_read else Colors.TEXT_SECONDARY,
            text_size=(220, None),
            halign="left",
            valign="middle",
            size_hint_y=1
        )
        body_label = Label(
            text=notif.get("body", ""),
            font_size=12,
            color=Colors.TEXT_SECONDARY,
            text_size=(220, None),
            halign="left",
            valign="middle",
            size_hint_y=1
        )
        
        content.add_widget(title_label)
        content.add_widget(body_label)
        
        self.add_widget(icon_label)
        self.add_widget(content)


class NotificationsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "notifications"
        self._store = JsonStore("notifications_store.json")
        
        layout = BoxLayout(orientation="vertical", padding=0, spacing=0)
        
        header = BoxLayout(
            size_hint_y=None,
            height="56dp",
            padding=10,
            background_color=Colors.PRIMARY
        )
        
        header.add_widget(Label(
            text="Notifications",
            font_size=20,
            color=(1, 1, 1, 1),
            size_hint_x=1
        ))
        
        clear_btn = Button(
            text="Tout effacer",
            size_hint_x=None,
            width="90dp",
            background_color=(0, 0, 0, 0),
            color=(1, 1, 1, 1),
            on_press=self.clear_all
        )
        
        header.add_widget(clear_btn)
        
        scroll = ScrollView(size_hint=(1, 1), do_scroll_x=False)
        self.notif_list = BoxLayout(
            orientation="vertical",
            padding=0,
            spacing=0,
            size_hint_y=None,
            height="0dp"
        )
        scroll.add_widget(self.notif_list)
        
        empty = BoxLayout(
            orientation="vertical",
            padding=40,
            spacing=20,
            size_hint=(1, 1)
        )
        empty.add_widget(Label(
            text="🔔",
            font_size=60,
            color=Colors.TEXT_SECONDARY
        ))
        empty.add_widget(Label(
            text="Aucune notification",
            font_size=16,
            color=Colors.TEXT_SECONDARY
        ))
        
        self.content_area = BoxLayout(orientation="vertical")
        self.content_area.add_widget(scroll)
        self.content_area.add_widget(empty)
        
        layout.add_widget(header)
        layout.add_widget(self.content_area)
        
        self.add_widget(layout)
        self._load_notifications()
    
    def _load_notifications(self):
        self.notif_list.clear_widgets()
        total_height = 0
        
        sample_notifs = [
            {"type": "trip", "title": "Trajet confirmé", "body": "Votre trajet vers Owendo est confirmé", "is_read": False},
            {"type": "payment", "title": "Paiement reçu", "body": "1,000 XAF reçu avec succès", "is_read": False},
            {"type": "driver", "title": "Conducteur en route", "body": "Votre conducteur arrive dans 5 min", "is_read": True},
        ]
        
        for notif in sample_notifs:
            item = NotifItem(notif)
            self.notif_list.add_widget(item)
            total_height += 80
        
        unread = sum(1 for n in sample_notifs if not n.get("is_read"))
        self.notif_list.height = total_height
        
        scroll = self.content_area.children[0]
        empty = self.content_area.children[1]
        scroll.opacity = 1 if total_height > 0 else 0
        empty.opacity = 0 if total_height > 0 else 1
    
    def clear_all(self, instance):
        self._load_notifications()