# ============================================================
# Écran Notation Client
# Fichier : mobile/screens/client/rating_screen.py
# Description : Note 1-5 étoiles + commentaire après trajet
# ============================================================

from kivy.uix.screen import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.slider import Slider
from mobile.theme.colors import Colors


STAR_TEMPLATE = """
#:set STAR "★"
#:set EMPTY "☆"

<StarButton@Button>:
    font_size: 36
    background_color: (0, 0, 0, 0)
    color: Colors.WARNING
    markup: True
    on_press: root.setter("star_val")(self.star_val)
"""


class RatingScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "rating"
        self._rating = 5
        
        layout = BoxLayout(
            orientation="vertical",
            padding=40,
            spacing=20
        )
        
        title = Label(
            text="Noter votre trajet",
            font_size=24,
            color=Colors.PRIMARY,
            size_hint_y=None,
            height=50
        )
        
        stars_layout = BoxLayout(
            size_hint_y=None,
            height="80dp",
            spacing=10
        )
        
        self._star_labels = []
        for i in range(5):
            lbl = Label(
                text="★",
                font_size=48,
                color=Colors.WARNING,
                markup=True,
                halign="center"
            )
            lbl._star_index = i
            stars_layout.add_widget(lbl)
            self._star_labels.append(lbl)
        
        self.rating_label = Label(
            text="5/5 - Excellent",
            font_size=16,
            color=Colors.TEXT_SECONDARY,
            size_hint_y=None,
            height=30
        )
        
        self.comment_input = TextInput(
            hint_text="Commentaire (optionnel)...",
            multiline=True,
            size_hint_y=0.3,
            font_size=14
        )
        
        feedback_items = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            height="200dp",
            spacing=8
        )
        
        feedback_labels = [
            "Ponctualité", "État du véhicule", "Courtoisie",
            "Respect du code de la route", "Propreté"
        ]
        
        self._feedback = {}
        for item in feedback_labels:
            row = BoxLayout(size_hint_y=None, height="36dp")
            row.add_widget(Label(text=item, color=Colors.TEXT_PRIMARY, size_hint_x=1, halign="left"))
            stars = BoxLayout(size_hint_x=None, width="150dp", spacing=4)
            for j in range(5):
                btn = Button(
                    text="○",
                    font_size=20,
                    background_color=(0, 0, 0, 0),
                    color=Colors.WARNING,
                    width="30dp",
                    on_press=lambda x, idx=j: self._set_feedback(item, idx)
                )
                stars.add_widget(btn)
            self._feedback[item] = 3
            row.add_widget(stars)
            feedback_items.add_widget(row)
        
        submit_btn = Button(
            text="Envoyer",
            background_color=Colors.ACCENT,
            color=(1, 1, 1, 1),
            size_hint_y=None,
            height="50dp",
            on_press=self.submit_rating
        )
        
        later_btn = Button(
            text="Plus tard",
            background_color=Colors.SURFACE,
            color=Colors.TEXT_SECONDARY,
            size_hint_y=None,
            height="50dp",
            on_press=self.skip
        )
        
        layout.add_widget(title)
        layout.add_widget(stars_layout)
        layout.add_widget(self.rating_label)
        layout.add_widget(Label(text="", size_hint_y=None, height=10))
        layout.add_widget(Label(
            text="Détails",
            color=Colors.TEXT_PRIMARY,
            size_hint_y=None,
            height=30
        ))
        layout.add_widget(feedback_items)
        layout.add_widget(self.comment_input)
        layout.add_widget(Label(text="", size_hint_y=0.1))
        layout.add_widget(submit_btn)
        layout.add_widget(later_btn)
        
        self.add_widget(layout)
    
    def _update_stars(self):
        labels = ["○", "○", "○", "○", "○"]
        for i in range(self._rating):
            labels[i] = "●"
        for i, lbl in enumerate(self._star_labels):
            lbl.text = labels[i]
        
        ratings = ["", "Mauvais", "Passable", "Correct", "Bon", "Excellent"]
        self.rating_label.text = f"{self._rating}/5 - {ratings[self._rating]}"
    
    def _set_feedback(self, item: str, value: int):
        self._feedback[item] = value + 1
    
    def submit_rating(self, instance):
        import httpx
        import mobile.config as config
        from mobile.services.auth_service import auth_service
        
        user_id = auth_service.get_user_id() or "current_user"
        
        try:
            httpx.post(
                f"{config.API_BASE_URL}/ratings",
                json={
                    "trip_id": "current_trip",
                    "user_id": user_id,
                    "rating": self._rating,
                    "comment": self.comment_input.text,
                    "feedback": self._feedback
                },
                timeout=config.API_TIMEOUT
            )
        except Exception:
            pass
        
        self.manager.current = "home"
    
    def skip(self, instance):
        self.manager.current = "home"