# ============================================================
# Écran Paramètres Mobile Kivy
# Fichier : mobile/screens/client/settings_screen.py
# Description : Écran de paramètres et configuration
# ============================================================

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.properties import BooleanProperty, StringProperty


class SettingsScreen(Screen):
    """Écran des paramètres MobiTranz."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "settings"
        self.build_ui()
    
    def build_ui(self):
        """Construction de l'interface utilisateur."""
        from kivy.uix.scrollview import ScrollView
        
        layout = BoxLayout(orientation="vertical", padding=20, spacing=10)
        
        layout.add_widget(Label(text="Paramètres", font_size=24, size_hint_y=None, height=50))
        
        scroll = ScrollView()
        content = BoxLayout(orientation="vertical", padding=10, spacing=15, size_hint_y=None)
        content.bind(minimum_height=content.setter('height'))
        
        content.add_widget(self._create_section("Compte"))
        content.add_widget(self._create_button("Modifier le profil", self.edit_profile))
        content.add_widget(self._create_button("Changer le mot de passe", self.change_password))
        content.add_widget(self._create_button("Gérer les méthodes de paiement", self.manage_payment))
        
        content.add_widget(self._create_section("Notifications"))
        content.add_widget(self._create_toggle("Notifications push", True, self.toggle_push))
        content.add_widget(self._create_toggle("Notifications SMS", True, self.toggle_sms))
        content.add_widget(self._create_toggle("Sons", True, self.toggle_sounds))
        
        content.add_widget(self._create_section("Confidentialité"))
        content.add_widget(self._create_toggle("Partage de position", True, self.toggle_location))
        content.add_widget(self._create_toggle("Historique de trajet", True, self.toggle_history))
        
        content.add_widget(self._create_section("Application"))
        content.add_widget(self._create_button("Langue", self.change_language))
        content.add_widget(self._create_button("Devise (XAF)", self.change_currency))
        content.add_widget(self._create_button("Aide et support", self.open_help))
        content.add_widget(self._create_button("Signaler un problème", self.report_issue))
        
        content.add_widget(self._create_section("À propos"))
        content.add_widget(self._create_button("Version 1.0.0", self.show_about))
        content.add_widget(self._create_button("Conditions d'utilisation", self.show_terms))
        content.add_widget(self._create_button("Politique de confidentialité", self.show_privacy))
        
        content.add_widget(self._create_button("Déconnexion", self.logout, color=(0.8, 0.2, 0.2, 1)))
        
        scroll.add_widget(content)
        layout.add_widget(scroll)
        
        self.add_widget(layout)
    
    def _create_section(self, title):
        """Crée un en-tête de section."""
        label = Label(
            text=title,
            font_size=16,
            bold=True,
            size_hint_y=None,
            height=40,
            color=(0, 0.6, 0.27, 1)
        )
        return label
    
    def _create_button(self, text, callback, color=(0, 0.6, 0.27, 1)):
        """Crée un bouton de paramètres."""
        btn = Button(
            text=text,
            size_hint_y=None,
            height=50,
            background_color=(0.95, 0.95, 0.95, 1),
            color=color
        )
        btn.bind(on_press=callback)
        return btn
    
    def _create_toggle(self, text, active, callback):
        """Crée un toggle de paramètres."""
        from kivy.uix.switch import Switch
        
        container = BoxLayout(size_hint_y=None, height=50)
        label = Label(text=text, size_hint_x=0.7)
        switch = Switch(active=active)
        switch.bind(on_active=callback)
        container.add_widget(label)
        container.add_widget(switch)
        return container
    
    def edit_profile(self, instance):
        print("Modifier le profil")
    
    def change_password(self, instance):
        print("Changer le mot de passe")
    
    def manage_payment(self, instance):
        print("Gérer les méthodes de paiement")
    
    def toggle_push(self, switch, value):
        print(f"Notifications push: {value}")
    
    def toggle_sms(self, switch, value):
        print(f"Notifications SMS: {value}")
    
    def toggle_sounds(self, switch, value):
        print(f"Sons: {value}")
    
    def toggle_location(self, switch, value):
        print(f"Partage de position: {value}")
    
    def toggle_history(self, switch, value):
        print(f"Historique de trajet: {value}")
    
    def change_language(self, instance):
        print("Changer la langue")
    
    def change_currency(self, instance):
        print("Changer la devise")
    
    def open_help(self, instance):
        print("Aide et support")
    
    def report_issue(self, instance):
        print("Signaler un problème")
    
    def show_about(self, instance):
        print("Version 1.0.0")
    
    def show_terms(self, instance):
        print("Conditions d'utilisation")
    
    def show_privacy(self, instance):
        print("Politique de confidentialité")
    
    def logout(self, instance):
        print("Déconnexion")
        self.manager.current = "login"