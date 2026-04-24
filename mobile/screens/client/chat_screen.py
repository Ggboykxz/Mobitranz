# ============================================================
# Écran Chat Client-Driver
# Fichier : mobile/screens/client/chat_screen.py
# Description : Messagerie entre client et driver
# ============================================================

from kivy.uix.screen import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.relativelayout import RelativeLayout
from kivy.properties import BooleanProperty
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
            background_color=bg_color,
            canvas.before={
                "Color": {"rgb": bg_color},
                "Rectangle": {"pos": self.pos, "size": self.size, "radius": [12, 12, 12, 12]},
            }
        )
        
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
        
        header = BoxLayout(
            size_hint_y=None,
            height="56dp",
            padding=10,
            background_color=Colors.PRIMARY
        )
        
        driver_label = Label(
            text="Conducteur",
            color=(1, 1, 1, 1),
            font_size=18,
            size_hint_x=1
        )
        
        back_btn = Button(
            text="←",
            size_hint_x=None,
            width="48dp",
            background_color=(0, 0, 0, 0),
            on_press=lambda x: setattr(self.manager, "current", "trip_active")
        )
        
        header.add_widget(back_btn)
        header.add_widget(driver_label)
        header.add_widget(Label(text="", size_hint_x=None, width="48dp"))
        
        self.messages_area = ScrollView(
            size_hint=(1, 1),
            do_scroll_x=False
        )
        self.messages_layout = BoxLayout(
            orientation="vertical",
            padding=10,
            spacing=8,
            size_hint_y=None,
            height="0dp"
        )
        self.messages_area.add_widget(self.messages_layout)
        
        input_bar = BoxLayout(
            size_hint_y=None,
            height="56dp",
            padding=8,
            spacing=8
        )
        
        self.msg_input = TextInput(
            hint_text="Message...",
            multiline=False,
            size_hint_x=1,
            font_size=14
        )
        
        send_btn = Button(
            text="Envoyer",
            width="80dp",
            size_hint_x=None,
            background_color=Colors.PRIMARY,
            color=(1, 1, 1, 1),
            on_press=self.send_message
        )
        
        input_bar.add_widget(self.msg_input)
        input_bar.add_widget(send_btn)
        
        layout.add_widget(header)
        layout.add_widget(self.messages_area)
        layout.add_widget(input_bar)
        
        self.add_widget(layout)
        
        self._add_message("Bonjour, je suis votre conducteur", False)
        self._add_message("Bien reçu, merci !", True)
    
    def _add_message(self, text: str, is_mine: bool):
        bubble = ChatBubble(text=text, is_mine=is_mine)
        self.messages_layout.add_widget(bubble)
        self._messages.append((text, is_mine))
        self.messages_layout.height = len(self._messages) * 70 + 10
    
    def send_message(self, instance):
        text = self.msg_input.text.strip()
        if not text:
            return
        self._add_message(text, True)
        self.msg_input.text = ""
        self.messages_area.scroll_y = 0