from kivy.clock import Clock
from kivy.uix.screenmanager import Screen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton, MDFlatButton, MDIconButton
from kivymd.uix.spinner import MDSpinner
from kivymd.uix.snackbar import MDSnackbar
from kivymd.uix.topappbar import MDTopAppBar
from kivymd.uix.scrollview import MDScrollView
from kivy.metrics import dp
from mobile.services.api_client import api_client
from mobile.services.cache_service import cache_service
from mobile.ui.shimmer import ShimmerBox
from mobile.ui.shimmer_list import ShimmerContainer
from mobile.ui.haptic import Haptic


NOTIFICATION_ICONS = {
    "trip": "car",
    "payment": "credit-card",
    "driver": "account",
    "sos": "alert",
    "system": "information",
    "promo": "tag",
}


class NotificationsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "notifications"
        self._notifications = []
        self._build_ui()

    def _build_ui(self):
        self.root = MDBoxLayout(orientation="vertical", md_bg_color="#F7F9FC")

        self.top_bar = MDTopAppBar(
            title="Notifications",
            md_bg_color="#1A3A6C",
            specific_text_color="#FFFFFF",
            left_action_items=[["arrow-left", lambda x: self.go_back()]],
            right_action_items=[["delete-sweep", lambda x: self.clear_all()]],
        )
        self.root.add_widget(self.top_bar)

        body = MDBoxLayout(orientation="vertical")

        self.scroll = MDScrollView(size_hint=(1, 1))
        self.notif_list = MDBoxLayout(
            orientation="vertical",
            padding=[8, 8],
            spacing=4,
            size_hint_y=None,
        )
        self.notif_list.bind(minimum_height=self.notif_list.setter("height"))
        self.scroll.add_widget(self.notif_list)
        body.add_widget(self.scroll)

        self.shimmer_layout = MDBoxLayout(
            orientation="vertical",
            padding=[8, 8],
            spacing=4,
            size_hint_y=None,
        )
        self.shimmer_layout.bind(minimum_height=self.shimmer_layout.setter("height"))
        for _ in range(3):
            card = MDCard(
                orientation="horizontal",
                size_hint_y=None,
                height=dp(72),
                padding=[12, 8],
                spacing=12,
                md_bg_color=[0.97, 0.97, 0.97, 1],
                radius=[8],
            )
            card.add_widget(ShimmerBox(width=28, height=28, radius=14))
            col = MDBoxLayout(orientation="vertical", spacing=4)
            col.add_widget(ShimmerBox(width=140, height=16))
            col.add_widget(ShimmerBox(width=200, height=14))
            col.add_widget(ShimmerBox(width=80, height=12))
            card.add_widget(col)
            self.shimmer_layout.add_widget(card)
        self.shimmer_layout.opacity = 0
        body.add_widget(self.shimmer_layout)

        self.empty_state = MDBoxLayout(
            orientation="vertical",
            adaptive_size=True,
            pos_hint={"center_x": 0.5, "center_y": 0.5},
            opacity=0,
        )
        empty_icon = MDIconButton(
            icon="bell-off",
            icon_color="#A0AEC0",
            theme_icon_size="Custom",
            icon_size=dp(64),
            pos_hint={"center_x": 0.5},
        )
        empty_label = MDLabel(
            text="Aucune notification",
            font_style="Subtitle1",
            theme_text_color="Secondary",
            halign="center",
        )
        self.empty_state.add_widget(empty_icon)
        self.empty_state.add_widget(empty_label)
        body.add_widget(self.empty_state)

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
        self.manager.switch("home")

    def show_offline_banner(self):
        if hasattr(self, '_offline_banner') and self._offline_banner:
            return
        self._offline_banner = MDLabel(
            text="⚠ Mode hors-ligne - Données en cache",
            size_hint_y=None,
            height=dp(30),
            md_bg_color="#FCD116",
            theme_text_color="Custom",
            text_color="#1A202C",
            halign="center",
            font_size=12,
        )
        self.add_widget(self._offline_banner)

    def hide_offline_banner(self):
        if hasattr(self, '_offline_banner') and self._offline_banner:
            if self._offline_banner.parent:
                self.remove_widget(self._offline_banner)
            self._offline_banner = None

    def on_enter(self):
        Clock.schedule_once(lambda dt: self.load_notifications())

    def on_leave(self):
        if self._notifications:
            cache_service.set("notifications", self._notifications)

    async def load_notifications(self):
        self.spinner.active = True
        self.shimmer_layout.opacity = 1
        self.notif_list.opacity = 0
        self.empty_state.opacity = 0
        self.hide_offline_banner()
        cached = cache_service.get("notifications")
        if cached:
            self._notifications = cached
            Clock.schedule_once(lambda dt: self.render_notifications())
        try:
            data = await api_client.get("/api/v1/notifications")
            self._notifications = data.get("notifications", data.get("data", []))
            cache_service.set("notifications", self._notifications)
            Clock.schedule_once(lambda dt: self.render_notifications())
            Clock.schedule_once(lambda dt: self.hide_offline_banner())
        except Exception:
            if not cached:
                stale = cache_service.get_stale("notifications")
                if stale:
                    self._notifications = stale
                    Clock.schedule_once(lambda dt: self.render_notifications())
                    Clock.schedule_once(lambda dt: self.show_offline_banner())
                else:
                    Clock.schedule_once(lambda dt: self.load_fallback())
        finally:
            Clock.schedule_once(lambda dt: setattr(self.spinner, "active", False))

    def load_fallback(self):
        self._notifications = [
            {"type": "trip", "title": "Trajet confirme", "body": "Votre trajet vers Owendo est confirme", "is_read": False, "created_at": "2026-05-12T10:30:00"},
            {"type": "payment", "title": "Paiement recu", "body": "1,000 XAF recu avec succes", "is_read": False, "created_at": "2026-05-12T09:15:00"},
            {"type": "driver", "title": "Conducteur en route", "body": "Votre conducteur arrive dans 5 min", "is_read": True, "created_at": "2026-05-11T18:00:00"},
        ]
        self.render_notifications()

    def render_notifications(self):
        self.shimmer_layout.opacity = 0
        self.notif_list.opacity = 1
        self.notif_list.clear_widgets()
        has_items = len(self._notifications) > 0

        for notif in self._notifications:
            item = self._build_notif_item(notif)
            self.notif_list.add_widget(item)

        self.empty_state.opacity = 0 if has_items else 1
        self.scroll.opacity = 1 if has_items else 0

    def _build_notif_item(self, notif):
        notif_type = notif.get("type", "system")
        icon = NOTIFICATION_ICONS.get(notif_type, "information")
        is_read = notif.get("is_read", False)
        title = notif.get("title", "Notification")
        body = notif.get("body", "")
        time = (notif.get("created_at") or "")[:16]

        bg = "#FFFFFF" if is_read else "#E8F0FE"
        icon_color = "#1A3A6C" if not is_read else "#A0AEC0"

        card = MDCard(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(72),
            padding=[12, 8],
            spacing=12,
            md_bg_color=bg,
            radius=[8],
            ripple_behavior=True,
        )
        card.bind(on_release=lambda x, n=notif: self.mark_read(n))

        icon_widget = MDIconButton(
            icon=icon,
            icon_color=icon_color,
            theme_icon_size="Custom",
            icon_size=dp(28),
        )
        card.add_widget(icon_widget)

        content = MDBoxLayout(orientation="vertical", spacing=2)
        content.add_widget(MDLabel(
            text=title,
            font_style="Subtitle2",
            theme_text_color="Primary",
            bold=not is_read,
            size_hint_y=None,
            height=dp(20),
        ))
        content.add_widget(MDLabel(
            text=body,
            font_style="Caption",
            theme_text_color="Secondary",
            size_hint_y=None,
            height=dp(18),
        ))
        if time:
            content.add_widget(MDLabel(
                text=time,
                font_style="Caption",
                theme_text_color="Custom",
                text_color="#A0AEC0",
                size_hint_y=None,
                height=dp(14),
            ))
        card.add_widget(content)

        if not is_read:
            dot = MDIconButton(
                icon="circle",
                icon_color="#1A3A6C",
                theme_icon_size="Custom",
                icon_size=dp(8),
                size_hint_x=None,
                width=dp(20),
            )
            card.add_widget(dot)

        return card

    async def mark_read(self, notif):
        notif_id = notif.get("id")
        if not notif_id:
            return
        try:
            await api_client.post(f"/api/v1/notifications/{notif_id}/read", {})
            Clock.schedule_once(lambda dt: self.load_notifications())
        except Exception as e:
            MDSnackbar(text=f"Erreur: {str(e)}", snackbar_x=10, snackbar_y=10).open()

    def clear_all(self):
        Clock.schedule_once(lambda dt: self.clear_all_api())

    async def clear_all_api(self):
        self.spinner.active = True
        try:
            await api_client.post("/api/v1/notifications/clear-all", {})
            self._notifications = []
            Clock.schedule_once(lambda dt: self.render_notifications())
            MDSnackbar(text="Toutes les notifications effacees", snackbar_x=10, snackbar_y=10).open()
        except Exception as e:
            MDSnackbar(text=f"Erreur: {str(e)}", snackbar_x=10, snackbar_y=10).open()
        finally:
            Clock.schedule_once(lambda dt: setattr(self.spinner, "active", False))
