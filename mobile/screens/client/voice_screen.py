import asyncio
from kivy.clock import Clock
from kivy.animation import Animation
from kivy.metrics import dp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDCard
from kivymd.uix.spinner import MDSpinner
from mobile.screens.base_screen import BaseScreen
from mobile.theme.theme import MobiTranzTheme
from mobile.services.kivy_api_client import kivy_api_client
from mobile.ui.haptic import Haptic
from mobile.ui.ripple import RippleButton


class VoiceScreen(BaseScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "voice"
        self._is_recording = False
        self._waveform_anim = None
        self._transcribed_data = None
        self._build_ui()

    def _build_ui(self):
        layout = MDBoxLayout(orientation="vertical", padding=20, spacing=16)

        header = MDBoxLayout(size_hint_y=None, height=60, adaptive_height=False)
        back_btn = MDFlatButton(
            text="←",
            font_size=24,
            md_bg_color=MobiTranzTheme.PRIMARY,
            theme_text_color="Custom",
            text_color="FFFFFF",
            size_hint_x=0.15,
            on_release=lambda x: self.manager.switch("home"),
        )
        title = MDLabel(
            text="Proposition Vocale",
            font_size=22,
            bold=True,
            halign="center",
            theme_text_color="Custom",
            text_color=MobiTranzTheme.PRIMARY,
            size_hint_x=0.7,
        )
        header.add_widget(back_btn)
        header.add_widget(title)
        layout.add_widget(header)

        instructions = MDLabel(
            text="Dites votre destination,\nle montant et le nombre de places\n\nExemple: \"Owendo mille francs deux places\"",
            font_size=14,
            halign="center",
            theme_text_color="Secondary",
        )
        layout.add_widget(instructions)

        self.waveform_card = MDCard(
            size_hint=(1, 0.35),
            md_bg_color=[0.95, 0.97, 0.99, 1],
            radius=[dp(16)],
            orientation="center",
        )
        self.waveform_icon = MDLabel(
            text="🎤",
            font_size=64,
            halign="center",
            valign="middle",
            theme_text_color="Custom",
            text_color=MobiTranzTheme.PRIMARY,
        )
        self.waveform_card.add_widget(self.waveform_icon)
        layout.add_widget(self.waveform_card)

        self.transcription_label = MDLabel(
            text="Appuyez sur le microphone pour commencer",
            font_size=14,
            halign="center",
            theme_text_color="Secondary",
        )
        layout.add_widget(self.transcription_label)

        self.result_card = MDCard(
            orientation="vertical",
            padding=12,
            spacing=6,
            size_hint_y=None,
            height=dp(100),
            md_bg_color=[0.93, 0.96, 0.98, 1],
            radius=[dp(8)],
            opacity=0,
        )
        self.dest_label = MDLabel(
            text="Destination: ---",
            font_size=14,
            theme_text_color="Primary",
        )
        self.amount_label = MDLabel(
            text="Montant: ---",
            font_size=14,
            theme_text_color="Primary",
        )
        self.seats_label = MDLabel(
            text="Places: ---",
            font_size=14,
            theme_text_color="Primary",
        )
        self.loading_label = MDLabel(
            text="",
            font_size=13,
            halign="center",
            theme_text_color="Secondary",
        )
        self.result_card.add_widget(self.dest_label)
        self.result_card.add_widget(self.amount_label)
        self.result_card.add_widget(self.seats_label)
        self.result_card.add_widget(self.loading_label)
        layout.add_widget(self.result_card)

        buttons = MDBoxLayout(size_hint_y=None, height=60, spacing=12)

        self.record_btn = RippleButton(
            text="🎤  Enregistrer",
            md_bg_color=MobiTranzTheme.DANGER,
            size_hint=(1, 1),
            on_release=self.toggle_recording,
        )
        self.send_btn = RippleButton(
            text="📤  Envoyer",
            md_bg_color=MobiTranzTheme.ACCENT,
            size_hint=(1, 1),
            on_release=self.send_proposal,
            disabled=True,
        )

        buttons.add_widget(self.record_btn)
        buttons.add_widget(self.send_btn)
        layout.add_widget(buttons)

        self.add_widget(layout)

    def on_enter(self):
        self._reset()

    def _reset(self):
        self._is_recording = False
        self._transcribed_data = None
        self.record_btn.text = "🎤  Enregistrer"
        self.record_btn.md_bg_color = MobiTranzTheme.DANGER
        self.record_btn.disabled = False
        self.send_btn.disabled = True
        self.send_btn.md_bg_color = MobiTranzTheme.ACCENT
        self.transcription_label.text = "Appuyez sur le microphone pour commencer"
        self.result_card.opacity = 0
        self.dest_label.text = "Destination: ---"
        self.amount_label.text = "Montant: ---"
        self.seats_label.text = "Places: ---"
        self.loading_label.text = ""
        self.waveform_icon.text = "🎤"
        self.waveform_icon.opacity = 1

    def toggle_recording(self, instance):
        self._is_recording = not self._is_recording

        if self._is_recording:
            Haptic.heavy()
            self.record_btn.text = "⏹  Arrêter"
            self.record_btn.md_bg_color = "#718096"
            self.transcription_label.text = "🎤 Écoute en cours..."
            self._start_waveform_animation()
        else:
            Haptic.medium()
            self.record_btn.text = "🎤  Enregistrer"
            self.record_btn.md_bg_color = MobiTranzTheme.DANGER
            self.record_btn.disabled = True
            self._stop_waveform_animation()
            self.transcription_label.text = "Transcription en cours..."
            self._simulate_transcription()

    def _start_waveform_animation(self):
        anim = Animation(opacity=0.3, duration=0.3) + Animation(opacity=1.0, duration=0.3)
        anim.repeat = True
        anim.start(self.waveform_icon)
        self._waveform_anim = anim

    def _stop_waveform_animation(self):
        if self._waveform_anim:
            self._waveform_anim.repeat = False
            self._waveform_anim.stop(self.waveform_icon)
            self._waveform_anim = None
        self.waveform_icon.opacity = 1.0

    def _simulate_transcription(self):
        def do_transcription(dt):
            self.transcription_label.text = "Owendo mille francs deux places"
            self.dest_label.text = "Destination: Owendo"
            self.amount_label.text = "Montant: 1000 XAF"
            self.seats_label.text = "Places: 2"
            self.result_card.opacity = 1
            self.record_btn.disabled = False
            self.send_btn.disabled = False
            self._transcribed_data = {
                "destination": "Owendo",
                "amount": 1000,
                "seats": 2,
                "transcription": "Owendo mille francs deux places",
            }

        Clock.schedule_once(do_transcription, 1.5)

    def send_proposal(self, instance):
        if not self._transcribed_data:
            self.show_toast("Aucune proposition à envoyer")
            return

        self.show_loading()

        def on_success(result):
            self.hide_loading()
            Haptic.medium()
            self.show_toast("Proposition envoyée avec succès!")
            Clock.schedule_once(lambda dt: self.manager.switch("home"), 1.5)

        def on_error(error):
            self.hide_loading()
            self.show_error("Erreur lors de l'envoi: " + str(error)[:80])

        kivy_api_client.call(
            "submit_voice_proposal",
            data=self._transcribed_data,
            on_success=on_success,
            on_error=on_error,
        )
