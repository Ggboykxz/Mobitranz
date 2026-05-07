# ============================================================
# Écran Chat Client-Driver
# Fichier : mobile/screens/client/chat_screen.py
# Description : Messagerie entre client et driver
# ============================================================

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.relativelayout import RelativeLayout
from kivy.properties import BooleanProperty
from kivy.graphics import Color, RoundedRectangle
from mobile.theme.colors import Colors


class ChatBubble(RelativeLayout):
    is_mine = BooleanProperty(False)
    
    def __init__(self, text: str, is_mine: bool = False, **kwargs):
        super().__init__(**kwargs)
        self.is_mine = is_mine
        self.size_hint = (None, None)
        self.size = ("260dp", "50dp")
        
        bg_color = Colors.PRIMARY if is_mine else Colors.SURFACE
        text_color = Colors.TEXT_PRIMARY
        halign = "right" if is_mine else "left"
        
        bg = BoxLayout(
            size_hint=(1, 1),
            padding=10,
            background_color=bg_color
        )
        
        with bg.canvas.before:
            Color(rgba=bg_color)
            RoundedRectangle(pos=bg.pos, size=bg.size, radius=[12, 12, 12, 12])
        
        label = Label(
            text=text[:200],
            color=text_color,
            halign=halign,
            valign="middle",
            text_size=(240, None),
            font_size=14
        )
        
        bg.add_widget(label)
        self.add_widget(bg)


class ChatScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "chat"
        self._messages = []
        
        layout = BoxLayout(orientation="vertical", padding=0, spacing=0)
        
        top_bar = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height="60dp",
            padding=15,
            spacing=10
        )
        top_bar.add_widget(Button(
            text="←",
            size_hint_x=None,
            width="50dp",
            on_press=self.go_back
        ))
        top_bar.add_widget(Label(text="Chat", font_size=20))
        
        self.messages_container = ScrollView(size_hint=(1, 1))
        self.messages_layout = BoxLayout(
            orientation="vertical",
            padding=15,
            spacing=10,
            size_hint_y=None
        )
        self.messages_layout.bind(minimum_height=self.messages_layout.setter('height'))
        self.messages_container.add_widget(self.messages_layout)
        
        input_bar = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height="60dp",
            padding=10,
            spacing=10
        )
        
        self.message_input = TextInput(
            hint_text="Tapez votre message...",
            size_hint_x=0.8,
            multiline=False
        )
        self.message_input.bind(on_text_validate=self.send_message)
        
        send_btn = Button(
            text="Envoyer",
            size_hint_x=0.2,
            background_color=Colors.PRIMARY,
            color=(1, 1, 1, 1),
            on_press=self.send_message
        )
        
        input_bar.add_widget(self.message_input)
        input_bar.add_widget(send_btn)
        
        layout.add_widget(top_bar)
        layout.add_widget(self.messages_container)
        layout.add_widget(input_bar)
        
        self.add_widget(layout)
    
    def go_back(self, instance):
        self.manager.current = "home"
    
    def send_message(self, instance):
        text = self.message_input.text.strip()
        if not text:
            return
        
        self._messages.append({"text": text, "is_mine": True})
        self.add_message(text, True)
        self.message_input.text = ""
        
        self._messages.append({"text": "Merci pour votre message!", "is_mine": False})
        self.add_message("Merci pour votre message!", False)
    
    def add_message(self, text: str, is_mine: bool):
        bubble = ChatBubble(text, is_mine)
        self.messages_layout.add_widget(bubble)
        self.messages_container.scroll_to(bubble)