from kivy.clock import Clock
from kivy.uix.screenmanager import Screen
from kivy.properties import BooleanProperty
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton, MDFlatButton, MDIconButton
from kivymd.uix.spinner import MDSpinner
from kivymd.uix.snackbar import MDSnackbar
from kivymd.uix.topappbar import MDTopAppBar
from kivymd.uix.textfield import MDTextField
from kivymd.uix.scrollview import MDScrollView
from kivy.metrics import dp
from mobile.services.api_client import api_client
from mobile.services.cache_service import cache_service


class ChatBubble(MDCard):
    is_mine = BooleanProperty(False)

    def __init__(self, text="", is_mine=False, **kwargs):
        super().__init__(**kwargs)
        self.is_mine = is_mine
        self.orientation = "vertical"
        self.size_hint_x = 0.75
        self.size_hint_y = None
        self.padding = [12, 8]
        self.spacing = 0
        self.radius = [12]
        self.elevation = 0

        if is_mine:
            self.md_bg_color = "#1A3A6C"
            self.pos_hint = {"right": 1}
            self.text_color = "#FFFFFF"
        else:
            self.md_bg_color = "#EDF2F7"
            self.pos_hint = {"left": 0}
            self.text_color = "#1A202C"

        self.add_widget(MDLabel(
            text=text[:500],
            font_style="Body2",
            theme_text_color="Custom",
            text_color=self.text_color,
            size_hint_y=None,
            text_size=(dp(240), None),
            halign="left" if not is_mine else "right",
        ))

        self.bind(minimum_height=self.setter("height"))

    def on_text(self, instance, value):
        pass


class ChatScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "chat"
        self._messages = []
        self._trip_id = None
        self._poll_event = None
        self._build_ui()

    def _build_ui(self):
        self.root = MDBoxLayout(orientation="vertical", md_bg_color="#F7F9FC")

        self.top_bar = MDTopAppBar(
            title="Chat",
            md_bg_color="#1A3A6C",
            specific_text_color="#FFFFFF",
            left_action_items=[["arrow-left", lambda x: self.go_back()]],
            right_action_items=[["phone", lambda x: self.call_driver()]],
        )
        self.root.add_widget(self.top_bar)

        self.scroll = MDScrollView(size_hint=(1, 1))
        self.messages_layout = MDBoxLayout(
            orientation="vertical",
            padding=[12, 8],
            spacing=8,
            size_hint_y=None,
            padding_top=8,
            padding_bottom=8,
        )
        self.messages_layout.bind(minimum_height=self.messages_layout.setter("height"))
        self.scroll.add_widget(self.messages_layout)
        self.root.add_widget(self.scroll)

        self.typing_label = MDLabel(
            text="",
            font_style="Caption",
            theme_text_color="Secondary",
            size_hint_y=None,
            height=dp(20),
            padding=[16, 0],
            opacity=0,
        )
        self.root.add_widget(self.typing_label)

        input_bar = MDCard(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(60),
            padding=[8, 8],
            spacing=8,
            md_bg_color="#FFFFFF",
            radius=[0],
            elevation=2,
        )

        self.message_input = MDTextField(
            hint_text="Tapez votre message...",
            mode="round",
            size_hint_x=0.8,
        )
        self.message_input.bind(on_text_validate=self.send_message)
        input_bar.add_widget(self.message_input)

        send_btn = MDIconButton(
            icon="send",
            icon_color="#1A3A6C",
            theme_icon_size="Custom",
            icon_size=dp(24),
            on_release=self.send_message,
        )
        input_bar.add_widget(send_btn)

        self.root.add_widget(input_bar)

        self.spinner = MDSpinner(
            size_hint=(None, None),
            size=(dp(24), dp(24)),
            pos_hint={"center_x": 0.5},
            active=False,
        )
        self.root.add_widget(self.spinner)

        self.add_widget(self.root)

    def go_back(self):
        if self._poll_event:
            self._poll_event.cancel()
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

    def call_driver(self):
        MDSnackbar(text="Appel en cours...", snackbar_x=10, snackbar_y=10).open()

    def on_enter(self):
        self._trip_id = getattr(self, "trip_id", None) or getattr(self.manager, "current_trip_id", None)
        if self._trip_id:
            self.load_messages()
            self._poll_event = Clock.schedule_interval(lambda dt: self.poll_messages(), 10)
        else:
            self.add_dummy_messages()

    def on_leave(self):
        if self._poll_event:
            self._poll_event.cancel()
            self._poll_event = None
        if self._messages:
            cache_service.set(f"chat_{self._trip_id}", self._messages)

    def add_dummy_messages(self):
        self.messages_layout.clear_widgets()
        demos = [
            ("Bonjour ! Je suis votre conducteur. Je arrive dans 5 minutes.", False),
            ("Tres bien, je vous attends devant le immeuble.", True),
            ("Parfait, je suis arrive. Vehicule blanche immatricule AA-001-AI.", False),
        ]
        for text, is_mine in demos:
            self.add_bubble(text, is_mine)
        Clock.schedule_once(lambda dt: self.scroll_to_bottom(), 0.1)

    async def load_messages(self):
        self.spinner.active = True
        self.hide_offline_banner()
        cache_key = f"chat_{self._trip_id}"
        cached = cache_service.get(cache_key)
        if cached:
            Clock.schedule_once(lambda dt: self.render_messages(cached))
        try:
            data = await api_client.get(f"/api/v1/trips/{self._trip_id}/messages")
            messages = data.get("messages", data.get("data", []))
            self._messages = messages
            cache_service.set(cache_key, messages)
            Clock.schedule_once(lambda dt: self.render_messages(messages))
            Clock.schedule_once(lambda dt: self.hide_offline_banner())
        except Exception:
            if not cached:
                stale = cache_service.get_stale(cache_key)
                if stale:
                    self._messages = stale
                    Clock.schedule_once(lambda dt: self.render_messages(stale))
                    Clock.schedule_once(lambda dt: self.show_offline_banner())
        finally:
            Clock.schedule_once(lambda dt: setattr(self.spinner, "active", False))

    async def poll_messages(self):
        try:
            data = await api_client.get(f"/api/v1/trips/{self._trip_id}/messages")
            messages = data.get("messages", data.get("data", []))
            if len(messages) > len(self._messages):
                Clock.schedule_once(lambda dt, msgs=messages: self.render_messages(msgs))
        except Exception:
            pass

    def render_messages(self, messages):
        self.messages_layout.clear_widgets()
        self._messages = messages
        for msg in messages:
            text = msg.get("content", msg.get("text", ""))
            is_mine = msg.get("sender", msg.get("role", "")) == "client"
            self.add_bubble(text, is_mine)
        Clock.schedule_once(lambda dt: self.scroll_to_bottom(), 0.1)

    def add_bubble(self, text, is_mine):
        height = max(dp(40), len(text) * 3)
        bubble = ChatBubble(text=text, is_mine=is_mine, height=height)
        self.messages_layout.add_widget(bubble)

    def scroll_to_bottom(self):
        if self.scroll and self.messages_layout:
            self.scroll.scroll_y = 0

    def send_message(self, instance):
        text = self.message_input.text.strip()
        if not text:
            return
        self.message_input.text = ""
        self.add_bubble(text, True)
        Clock.schedule_once(lambda dt: self.scroll_to_bottom(), 0.1)
        Clock.schedule_once(lambda dt: self.send_to_api(text))

    async def send_to_api(self, text):
        self.spinner.active = True
        try:
            await api_client.post("/api/v1/messages", {
                "trip_id": self._trip_id or "demo",
                "content": text,
                "sender": "client",
            })
            self.show_typing_indicator()
        except Exception as e:
            MDSnackbar(text=f"Erreur envoi: {str(e)}", snackbar_x=10, snackbar_y=10).open()
        finally:
            self.spinner.active = False

    def show_typing_indicator(self):
        self.typing_label.text = "Conducteur ecrit..."
        self.typing_label.opacity = 1
        Clock.schedule_once(lambda dt: self.hide_typing_indicator(), 2)

    def hide_typing_indicator(self):
        self.typing_label.opacity = 0
