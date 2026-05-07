# ============================================================
# Écran Scanner QR Code
# Fichier : mobile/screens/client/qr_scanner_screen.py
# ============================================================

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from mobile.theme.colors import Colors


class QRScannerScreen(Screen):
    """Écran scanner QR Code."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "qr_scanner"
        self._build_ui()
    
    def _build_ui(self):
        layout = BoxLayout(orientation="vertical", padding=20, spacing=16)
        
        # Header
        header = BoxLayout(size_hint_y=None, height=60)
        back_btn = Button(text="←", size_hint_x=0.15, background_color=Colors.SURFACE,
                       on_press=lambda x: setattr(self.manager, 'current', 'home'))
        title = Label(text="📷 Scanner QR", font_size=20, color=Colors.PRIMARY, size_hint_x=0.7)
        header.add_widget(back_btn)
        header.add_widget(title)
        layout.add_widget(header)
        
        # Camera preview area
        camera_area = BoxLayout(size_hint=(1, 0.6), background_color=Colors.GREY_800, radius=[12])
        camera_label = Label(text="📷\n\nCadrez le QR Code\ndu taxi", font_size=16, color=Colors.TEXT_SECONDARY, halign="center")
        camera_area.add_widget(camera_label)
        layout.add_widget(camera_area)
        
        # Status
        status = Label(text="Alignez le QR Code dans le cadre", font_size=14, color=Colors.TEXT_SECONDARY)
        layout.add_widget(status)
        
        # Result area
        self.result_area = BoxLayout(size_hint_y=None, height=80, opacity=0, background_color=Colors.GREY_100, radius=[8])
        self.result_label = Label(text="", font_size=14, color=Colors.TEXT_PRIMARY)
        self.result_area.add_widget(self.result_label)
        layout.add_widget(self.result_area)
        
        # Manual entry
        manual_btn = Button(text="Saisir manuellement", background_color=Colors.SURFACE,
                          color=Colors.PRIMARY, height=44)
        manual_btn.bind(on_press=self.show_manual_input)
        layout.add_widget(manual_btn)
        
        self.add_widget(layout)
    
    def show_manual_input(self, instance):
        """Affiche l'entrée manuelle."""
        self.result_label.text = "Saisie manuelle activée\nAA-001-AI"
        self.result_area.opacity = 1