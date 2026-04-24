# ============================================================
# Écran Profil Client
# Fichier : mobile/screens/client/profile_screen.py
# ============================================================

from kivy.uix.screen import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from mobile.theme.colors import Colors


class ProfileScreen(Screen):
    """Écran de profil client."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "profile"
        self._build_ui()
    
    def _build_ui(self):
        layout = BoxLayout(orientation="vertical", padding=20, spacing=16)
        
        # Header
        header = BoxLayout(size_hint_y=None, height=60)
        back_btn = Button(text="←", size_hint_x=0.15, background_color=Colors.SURFACE,
                       on_press=lambda x: setattr(self.manager, 'current', 'home'))
        title = Label(text="👤 Profil", font_size=20, color=Colors.PRIMARY, size_hint_x=0.7)
        header.add_widget(back_btn)
        header.add_widget(title)
        layout.add_widget(header)
        
        # Avatar
        avatar = BoxLayout(size_hint=(None, None), size=(100, 100), background_color=Colors.PRIMARY, radius=[50])
        avatar.add_widget(Label(text="JD", font_size=32, color=(1,1,1,1)))
        layout.add_widget(avatar)
        
        # Info
        info = BoxLayout(orientation="vertical", spacing=8)
        info.add_widget(Label(text="Jean Doe", font_size=20, color=Colors.TEXT_PRIMARY))
        info.add_widget(Label(text="+241 05 00 00 01", font_size=14, color=Colors.TEXT_SECONDARY))
        info.add_widget(Label(text="jean.doe@email.com", font_size=14, color=Colors.TEXT_SECONDARY))
        layout.add_widget(info)
        
        # Stats
        stats = BoxLayout(size_hint_y=None, height=80, background_color=Colors.SURFACE, radius=[12])
        for label, value in [("Trajets", "24"), ("Dépensé", "45K"), ("Note", "⭐4.8")]:
            col = BoxLayout(orientation="vertical")
            col.add_widget(Label(text=value, font_size=18, color=Colors.PRIMARY, bold=True))
            col.add_widget(Label(text=label, font_size=12, color=Colors.TEXT_SECONDARY))
            stats.add_widget(col)
        layout.add_widget(stats)
        
        # Menu items
        menu_items = [
            ("📝 Modifier profil", lambda x: None),
            ("🔔 Notifications", lambda x: None),
            ("💳 Moyens de paiement", lambda x: None),
            ("🔒 Sécurité", lambda x: None),
            ("❓ Aide", lambda x: None),
            ("🚪 Déconnexion", self.logout),
        ]
        
        for text, action in menu_items:
            btn = Button(text=text, height=48, background_color=Colors.SURFACE, color=Colors.TEXT_PRIMARY,
                       border=(0,0,0,0), on_press=action)
            layout.add_widget(btn)
        
        self.add_widget(layout)
    
    def logout(self, instance):
        """Déconnexion."""
        self.manager.current = "login"