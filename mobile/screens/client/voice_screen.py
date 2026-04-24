# ============================================================
# Écran Proposition Vocale Mobile
# Fichier : mobile/screens/client/voice_screen.py
# Description : Écran de proposition vocale avec enregistrement
# ============================================================

from kivy.uix.screen import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.animation import Animation
from mobile.theme.colors import Colors
import threading


class VoiceScreen(Screen):
    """Écran de proposition vocale MobiTranz.
    
    Permet d'enregistrer une proposition vocale et voir
    la transcription en temps réel.
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "voice"
        self._is_recording = False
        self._build_ui()
    
    def _build_ui(self):
        layout = BoxLayout(orientation="vertical", padding=20, spacing=16)
        
        # Header
        header = BoxLayout(size_hint_y=None, height=60)
        back_btn = Button(text="←", size_hint_x=0.15, background_color=Colors.SURFACE,
                       on_press=lambda x: setattr(self.manager, 'current', 'home'))
        title = Label(text="🎤 Proposition Vocale", font_size=20, color=Colors.PRIMARY, size_hint_x=0.7)
        header.add_widget(back_btn)
        header.add_widget(title)
        layout.add_widget(header)
        
        # Instructions
        instructions = Label(
            text="Dites votre destination,\nle montant et le nombre de places\n\nExemple: \"Owendo mille francs deux places\"",
            font_size=14, color=Colors.TEXT_SECONDARY, halign="center"
        )
        layout.add_widget(instructions)
        
        # Zone de visualisation
        self.waveform_area = BoxLayout(size_hint=(1, 0.4), background_color=Colors.SURFACE, radius=[12])
        self.waveform_label = Label(text="🎤", font_size=48, color=Colors.PRIMARY)
        self.waveform_area.add_widget(self.waveform_label)
        layout.add_widget(self.waveform_area)
        
        # Transcription
        self.transcription_label = Label(
            text="Appuyez sur le mikrophone pour commencer",
            font_size=14, color=Colors.TEXT_SECONDARY, halign="center"
        )
        layout.add_widget(self.transcription_label)
        
        # Extraction result
        self.result_area = BoxLayout(size_hint_y=None, height=100, opacity=0)
        result_card = BoxLayout(orientation="vertical", padding=10, background_color=Colors.GREY_100, radius=[8])
        
        self.dest_label = Label(text="Destination: ---", font_size=14, color=Colors.TEXT_PRIMARY)
        self.amount_label = Label(text="Montant: ---", font_size=14, color=Colors.TEXT_PRIMARY)
        self.seats_label = Label(text="Places: ---", font_size=14, color=Colors.TEXT_PRIMARY)
        
        result_card.add_widget(self.dest_label)
        result_card.add_widget(self.amount_label)
        result_card.add_widget(self.seats_label)
        self.result_area.add_widget(result_card)
        layout.add_widget(self.result_area)
        
        # Boutons
        buttons = BoxLayout(size_hint_y=None, height=60, spacing=12)
        
        self.record_btn = Button(
            text="🎤 Enregistrer",
            background_color=Colors.DANGER,
            color=(1,1,1,1),
            on_press=self.toggle_recording
        )
        self.send_btn = Button(
            text="📤 Envoyer",
            background_color=Colors.ACCENT,
            color=(1,1,1,1),
            on_press=self.send_proposal,
            disabled=True
        )
        
        buttons.add_widget(self.record_btn)
        buttons.add_widget(self.send_btn)
        layout.add_widget(buttons)
        
        self.add_widget(layout)
    
    def toggle_recording(self, instance):
        """Bascule l'enregistrement."""
        self._is_recording = not self._is_recording
        
        if self._is_recording:
            self.record_btn.text = "⏹ Arrêter"
            self.record_btn.background_color = Colors.GREY_500
            self.transcription_label.text = "🎤 Écoute en cours..."
            self._animate_waveform()
        else:
            self.record_btn.text = "🎤 Enregistrer"
            self.record_btn.background_color = Colors.DANGER
            self.transcription_label.text = "Transcription en cours..."
            self._simulate_transcription()
    
    def _animate_waveform(self):
        """Anime la zone de visualisation."""
        def pulse():
            if self._is_recording:
                Animation(opacity=0.5, duration=0.3).start(self.waveform_label)
                self.waveform_label.opacity = 1
        threading.Thread(target=pulse, daemon=True).start()
    
    def _simulate_transcription(self):
        """Simule une transcription."""
        def process():
            import time
            time.sleep(1)
            self.transcription_label.text = "Owendo mille francs deux places"
            self.dest_label.text = "Destination: Owendo"
            self.amount_label.text = "Montant: 1000 XAF"
            self.seats_label.text = "Places: 2"
            self.result_area.opacity = 1
            self.send_btn.disabled = False
        threading.Thread(target=process, daemon=True).start()
    
    def send_proposal(self, instance):
        """Envoie la proposition."""
        self.manager.current = "home"