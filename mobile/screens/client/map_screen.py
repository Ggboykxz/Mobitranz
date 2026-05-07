# ============================================================
# Écran Carte Mobile Kivy
# Fichier : mobile/screens/client/map_screen.py
# Description : Écran de carte et localisation
# ============================================================

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.graphics import Color, Rectangle


class MapScreen(Screen):
    """Écran de carte MobiTranz.
    
    Affiche la carte avec la position de l'utilisateur,
    les chauffeurs disponibles à proximité et les zones.
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "map"
        self.user_lat = 0.4163
        self.user_lon = 9.4673
        self.build_ui()
    
    def build_ui(self):
        """Construction de l'interface utilisateur."""
        layout = BoxLayout(orientation="vertical")
        
        top_bar = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=60,
            padding=10
        )
        top_bar.add_widget(Button(
            text="←",
            size_hint_x=None,
            width=50,
            on_press=self.go_back
        ))
        top_bar.add_widget(Label(text="Carte", font_size=20))
        
        map_container = BoxLayout()
        
        self.map_label = Label(
            text="[b]Carte MobiTranz[/b]\n\nPosition: 0.4163, 9.4673\nLibreville, Gabon\n\n Chauffeurs à proximité: 5\nZones: Centre Ville, Owendo, Akanda",
            markup=True,
            font_size=16,
            halign="center",
            valign="middle"
        )
        map_container.add_widget(self.map_label)
        
        info_panel = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            height=150,
            padding=10,
            spacing=5
        )
        
        info_panel.add_widget(self._create_info_card("Votre position", "Libreville, Centre Ville"))
        info_panel.add_widget(self._create_info_card("Chauffeurs proches", "5 disponibles"))
        info_panel.add_widget(self._create_info_card("Zone tarifaire", "Centre Ville - 500 XAF"))
        
        button_bar = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=60,
            padding=10,
            spacing=10
        )
        
        btn_locate = Button(
            text="Me localiser",
            background_color=(0, 0.6, 0.27, 1),
            color=(1, 1, 1, 1)
        )
        btn_locate.bind(on_press=self.locate_user)
        
        btn_search = Button(
            text="Rechercher",
            background_color=(0.99, 0.82, 0.09, 1),
            color=(0, 0, 0, 1)
        )
        btn_search.bind(on_press=self.search_location)
        
        button_bar.add_widget(btn_locate)
        button_bar.add_widget(btn_search)
        
        layout.add_widget(top_bar)
        layout.add_widget(map_container)
        layout.add_widget(info_panel)
        layout.add_widget(button_bar)
        
        self.add_widget(layout)
    
    def _create_info_card(self, title, value):
        """Crée une carte d'information."""
        from kivy.uix.relativelayout import RelativeLayout
        from kivy.graphics import Color, RoundedRectangle
        
        card = RelativeLayout(size_hint_y=None, height=40)
        
        with card.canvas:
            Color(0.95, 0.95, 0.95, 1)
            RoundedRectangle(pos=card.pos, size=card.size, radius=[5])
        
        label = Label(
            text=f"[b]{title}:[/b] {value}",
            markup=True,
            size_hint_x=0.9,
            x=10
        )
        card.add_widget(label)
        
        return card
    
    def go_back(self, instance):
        """Retour à l'écran précédent."""
        self.manager.current = "home"
    
    def locate_user(self, instance):
        """Localise l'utilisateur."""
        self.map_label.text = (
            "[b]Carte MobiTranz[/b]\n\n"
            "Position: 0.4163, 9.4673\n"
            "Libreville, Gabon\n\n"
            "🔄 Localisation en cours..."
        )
    
    def search_location(self, instance):
        """Recherche une position."""
        self.map_label.text = (
            "[b]Carte MobiTranz[/b]\n\n"
            "Recherche de position...\n\n"
            "Tapez votre destination"
        )
    
    def update_location(self, lat, lon):
        """Met à jour la position de l'utilisateur.
        
        Args:
            lat: Latitude
            lon: Longitude
        """
        self.user_lat = lat
        self.user_lon = lon
        
        self.map_label.text = (
            f"[b]Carte MobiTranz[/b]\n\n"
            f"Position: {lat}, {lon}\n"
            f"Libreville, Gabon\n\n"
            "Chauffeurs à proximité: 5\n"
            "Zones: Centre Ville, Owendo, Akanda"
        )
    
    def show_drivers(self, drivers):
        """Affiche les chauffeurs sur la carte.
        
        Args:
            drivers: Liste des chauffeurs proches
        """
        driver_text = "\n".join([
            f"• {d.get('name', 'Chauffeur')} - {d.get('distance', '1.2')} km"
            for d in drivers
        ])
        
        self.map_label.text = (
            f"[b]Carte MobiTranz[/b]\n\n"
            f"Position: {self.user_lat}, {self.user_lon}\n\n"
            f"[b]Chauffeurs à proximité:[/b]\n{driver_text}"
        )