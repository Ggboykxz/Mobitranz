from kivy.clock import Clock
from kivy.metrics import dp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from mobile.screens.base_screen import BaseScreen
from mobile.theme.theme import MobiTranzTheme
from mobile.services.kivy_api_client import kivy_api_client


class RatingScreen(BaseScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "rating"
        self._rating = 5
        self._star_labels = []
        self._feedback = {}
        self._build_ui()

    def _build_ui(self):
        layout = MDBoxLayout(orientation="vertical", padding=40, spacing=16)

        title = MDLabel(
            text="Noter votre trajet",
            font_size=24,
            halign="center",
            bold=True,
            theme_text_color="Custom",
            text_color=MobiTranzTheme.PRIMARY,
            size_hint_y=None,
            height=50,
        )
        layout.add_widget(title)

        stars_layout = MDBoxLayout(
            size_hint_y=None,
            height=dp(60),
            spacing=8,
            pos_hint={"center_x": 0.5},
        )

        for i in range(5):
            lbl = MDLabel(
                text="★",
                font_size=48,
                halign="center",
                theme_text_color="Custom",
                text_color=MobiTranzTheme.WARNING,
            )
            lbl._star_index = i
            lbl.bind(on_touch_down=self._make_star_tap(i))
            stars_layout.add_widget(lbl)
            self._star_labels.append(lbl)
        layout.add_widget(stars_layout)

        self.rating_label = MDLabel(
            text="5/5 - Excellent",
            font_size=16,
            halign="center",
            theme_text_color="Secondary",
            size_hint_y=None,
            height=30,
        )
        layout.add_widget(self.rating_label)

        self.comment_input = MDTextField(
            hint_text="Commentaire (optionnel)...",
            mode="rectangle",
            multiline=True,
            size_hint_y=None,
            height=dp(120),
        )
        layout.add_widget(self.comment_input)

        feedback_section = MDBoxLayout(
            orientation="vertical",
            size_hint_y=None,
            height=dp(200),
            spacing=8,
        )

        feedback_title = MDLabel(
            text="Détails",
            font_size=16,
            bold=True,
            theme_text_color="Primary",
            size_hint_y=None,
            height=30,
        )
        feedback_section.add_widget(feedback_title)

        feedback_labels = [
            "Ponctualité",
            "État du véhicule",
            "Courtoisie",
            "Respect du code",
            "Propreté",
        ]

        for item in feedback_labels:
            row = MDBoxLayout(size_hint_y=None, height=dp(32), spacing=4)
            row.add_widget(
                MDLabel(
                    text=item,
                    theme_text_color="Primary",
                    font_size=13,
                    size_hint_x=0.6,
                    halign="left",
                )
            )
            stars_row = MDBoxLayout(size_hint_x=0.4, spacing=2)
            for j in range(5):
                btn = MDFlatButton(
                    text="○",
                    font_size=18,
                    theme_text_color="Custom",
                    text_color=MobiTranzTheme.WARNING,
                    size_hint_x=None,
                    width=dp(28),
                    on_release=self._make_feedback_callback(item, j),
                )
                stars_row.add_widget(btn)
            self._feedback[item] = 3
            row.add_widget(stars_row)
            feedback_section.add_widget(row)
        layout.add_widget(feedback_section)

        layout.add_widget(MDBoxLayout(size_hint_y=None, height=dp(10)))

        submit_btn = MDRaisedButton(
            text="Envoyer",
            size_hint=(1, None),
            height=dp(50),
            md_bg_color=MobiTranzTheme.ACCENT,
            on_release=self.submit_rating,
        )
        layout.add_widget(submit_btn)

        later_btn = MDFlatButton(
            text="Plus tard",
            size_hint=(1, None),
            height=dp(50),
            theme_text_color="Custom",
            text_color=MobiTranzTheme.PRIMARY,
            on_release=self.skip,
        )
        layout.add_widget(later_btn)

        self.add_widget(layout)

        self._update_stars()

    def _make_star_tap(self, index):
        def on_touch(instance, touch):
            if instance.collide_point(*touch.pos):
                self._rating = index + 1
                self._update_stars()
        return on_touch

    def _make_feedback_callback(self, item, star_index):
        def callback(instance):
            self._set_feedback(item, star_index + 1)
        return callback

    def _update_stars(self):
        for i, lbl in enumerate(self._star_labels):
            lbl.text = "★" if i < self._rating else "☆"

        ratings_labels = ["", "Mauvais", "Passable", "Correct", "Bon", "Excellent"]
        self.rating_label.text = f"{self._rating}/5 - {ratings_labels[self._rating]}"

    def _set_feedback(self, item, value):
        self._feedback[item] = value

    def submit_rating(self, instance):
        self.show_loading()
        data = {
            "trip_id": "current_trip",
            "rating": self._rating,
            "comment": self.comment_input.text.strip(),
            "feedback": self._feedback,
        }

        def on_success(result):
            self.hide_loading()
            self.show_toast("Note envoyée, merci!")
            Clock.schedule_once(lambda dt: self.manager.switch("home"), 1.5)

        def on_error(error):
            self.hide_loading()
            self.show_error("Erreur lors de l'envoi")

        kivy_api_client.call(
            "submit_rating",
            data=data,
            on_success=on_success,
            on_error=on_error,
        )

    def skip(self, instance):
        self.manager.switch("home")
