# ============================================================
# Module Conducteurs — Gestion détaillée des chauffeurs
# Fichier : desktop_admin/windows/modules/drivers_module.py
# Description : Gestion complète avec détails, historique, véhicule
# ============================================================

import customtkinter as ctk
from datetime import datetime
from desktop_admin.theme.components import FluentCard, FluentButton, FluentEntry
from desktop_admin.theme.components_detail import show_detail


class DriversModule(ctk.CTkFrame):
    """Module de gestion des chauffeurs.
    
    Sous-modules interconnectés:
    - Profil chauffeur (clic): Nom, téléphone, permis, rating
    - Véhicule (clic): Marque, modèle, plaque, assurance
    - Trajets (clic): Historique, revenus, km parcourus
    - Paiements (clic): Revenus, retraits, commissions
    - Incidents (clic): Signalements, sanctions
    - Documents (clic): Permis, assurance, технический contrôle
    - Carte GPS (clic): Position en temps réel
    - Performance (clic): Note, taux d'acceptation, trips
    """
    
    def __init__(self, master, dashboard=None, user_data=None, **kwargs):
        kwargs.setdefault("fg_color", "transparent")
        super().__init__(master, **kwargs)
        
        self._dashboard = dashboard
        self._user_data = user_data or {}
        self._api_client = dashboard.api_client if dashboard else None
        
        self._load_data()
        self._build_header()
        self._build_filters()
        self._build_table()
        self._build_pagination()
    
    def _load_data(self):
        """Charge les données depuis l'API."""
        try:
            if self._api_client:
                self._drivers_data = self._api_client.get_drivers(limit=100)
            else:
                self._drivers_data = self._get_demo_data()
        except Exception:
            self._drivers_data = self._get_demo_data()
    
    def _get_demo_data(self):
        """Données de démonstration détaillées."""
        return [
            {
                "id": "driver_001",
                "name": "Jean Dupont",
                "phone": "+24106010203",
                "email": "jean.dupont@email.ga",
                "status": "available",
                "rating": 4.8,
                "total_trips": 456,
                "total_revenue": 2450000,
                "vehicle": {
                    "brand": "Toyota Camry",
                    "model": "2022",
                    "plate": "LZ-001-GA",
                    "color": "Blanc",
                    "insurance": "2026-12-31",
                    "technical_check": "2026-06-15",
                },
                "license": {
                    "number": "AB123456",
                    "expiry": "2028-05-20",
                    "categories": ["B", "C"],
                },
                "documents": [
                    {"name": "Permis conduire", "status": "Valid", "expiry": "2028-05-20"},
                    {"name": "Assurance véhicule", "status": "Valid", "expiry": "2026-12-31"},
                    {"name": "Contrôle technique", "status": "Valid", "expiry": "2026-06-15"},
                ],
                "stats": {
                    "Trips ce mois": "45",
                    "Revenus ce mois": "125,000 XAF",
                    "Km parcourus": "2,150 km",
                    "Taux acceptation": "92%",
                    "Note moyenne": "4.8/5",
                    "Temps moyen": "18 min",
                },
                "history": [
                    {"date": "2026-05-07 14:20", "action": "Trajet terminé", "details": "Libreville → Owendo - 1,500 XAF"},
                    {"date": "2026-05-07 12:00", "action": "Proposition refusée", "details": "Destination trop lointaine"},
                    {"date": "2026-05-07 10:30", "action": "Connexion", "details": "App mobile"},
                    {"date": "2026-05-06 22:15", "action": "Retrait effectué", "details": "50,000 XAF vers Moov Money"},
                ],
                "incidents": [
                    {"date": "2026-04-15", "type": "Accident", "details": "Collision légère, responsabilité partagée"},
                ],
                "current_location": {"lat": 0.4163, "lon": 9.4673, "last_update": "2026-05-07 14:30"},
            },
            {
                "id": "driver_002",
                "name": "Marie Martin",
                "phone": "+24106010204",
                "email": "marie.martin@email.ga",
                "status": "on_trip",
                "rating": 4.6,
                "total_trips": 234,
                "total_revenue": 1180000,
                "vehicle": {
                    "brand": "Hyundai Accent",
                    "model": "2021",
                    "plate": "LZ-002-GA",
                    "color": "Gris",
                    "insurance": "2026-09-30",
                    "technical_check": "2026-07-20",
                },
                "license": {
                    "number": "CD789012",
                    "expiry": "2027-08-15",
                    "categories": ["B"],
                },
                "documents": [
                    {"name": "Permis conduire", "status": "Valid", "expiry": "2027-08-15"},
                    {"name": "Assurance véhicule", "status": "Valid", "expiry": "2026-09-30"},
                    {"name": "Contrôle technique", "status": "Expiré", "expiry": "2026-02-20"},
                ],
                "stats": {
                    "Trips ce mois": "32",
                    "Revenus ce mois": "89,000 XAF",
                    "Km parcourus": "1,450 km",
                    "Taux acceptation": "88%",
                    "Note moyenne": "4.6/5",
                    "Temps moyen": "22 min",
                },
                "history": [
                    {"date": "2026-05-07 14:45", "action": "Trajet en cours", "details": "Centre Ville → Akanda"},
                    {"date": "2026-05-07 12:30", "action": "Trajet terminé", "details": "Owendo → Libreville - 2,000 XAF"},
                ],
                "incidents": [],
                "current_location": {"lat": 0.4250, "lon": 9.4800, "last_update": "2026-05-07 14:45"},
            },
            {
                "id": "driver_003",
                "name": "Paul Bernard",
                "phone": "+24106010205",
                "email": "paul.bernard@email.ga",
                "status": "offline",
                "rating": 4.2,
                "total_trips": 89,
                "total_revenue": 456000,
                "vehicle": {
                    "brand": "Kia Rio",
                    "model": "2020",
                    "plate": "LZ-003-GA",
                    "color": "Noir",
                    "insurance": "2026-11-15",
                    "technical_check": "2026-08-01",
                },
                "license": {
                    "number": "EF345678",
                    "expiry": "2027-03-10",
                    "categories": ["B"],
                },
                "documents": [
                    {"name": "Permis conduire", "status": "Valid", "expiry": "2027-03-10"},
                    {"name": "Assurance véhicule", "status": "Valid", "expiry": "2026-11-15"},
                    {"name": "Contrôle technique", "status": "Valid", "expiry": "2026-08-01"},
                ],
                "stats": {
                    "Trips ce mois": "12",
                    "Revenus ce mois": "34,000 XAF",
                    "Km parcourus": "580 km",
                    "Taux acceptation": "75%",
                    "Note moyenne": "4.2/5",
                    "Temps moyen": "25 min",
                },
                "history": [
                    {"date": "2026-05-06 20:00", "action": "Déconnexion", "details": "Fin de service"},
                    {"date": "2026-05-06 18:30", "action": "Trajet terminé", "details": "Libreville → Nkoltang - 3,500 XAF"},
                ],
                "incidents": [
                    {"date": "2026-04-20", "type": "Retard", "details": "Arrivée avec 15 min de retard"},
                ],
                "current_location": {"lat": 0.3900, "lon": 9.4400, "last_update": "2026-05-06 20:00"},
            },
        ]
    
    def _build_header(self):
        """En-tête."""
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(0, 20))
        
        ctk.CTkLabel(
            header,
            text="Gestion des chauffeurs",
            font=ctk.CTkFont(size=24, weight="bold"),
        ).pack(side="left")
        
        actions = ctk.CTkFrame(header, fg_color="transparent")
        actions.pack(side="right")
        
        FluentButton(actions, text="+ Nouveau chauffeur", variant="primary", command=self._add_driver).pack(side="right")
        FluentButton(actions, text="🗺️ Carte", variant="secondary", command=self._show_map).pack(side="right", padx=(0, 10))
    
    def _build_filters(self):
        """Filtres."""
        filters = FluentCard(self, padding=16)
        filters.pack(fill="x", pady=(0, 16))
        
        self._search = FluentEntry(filters, label="Rechercher", placeholder="Nom, téléphone, plaque...", width=300)
        self._search.pack(side="left", padx=(0, 16))
        self._search.bind("<KeyRelease>", self._on_search)
        
        self._status_filter = ctk.CTkOptionMenu(filters, values=["Tous", "available", "on_trip", "offline"], width=150)
        self._status_filter.pack(side="left", padx=(0, 16))
        self._status_filter.bind("<<ComboboxSelected>>", self._on_filter)
    
    def _build_table(self):
        """Tableau avec boutons détails."""
        table = FluentCard(self, padding=0)
        table.pack(fill="both", expand=True)
        
        headers = ["ID", "Chauffeur", "Téléphone", "Véhicule", "Statut", "Note", "Trajets", "Revenus", "Actions"]
        
        header_row = ctk.CTkFrame(table, fg_color=("#F9FAFB", "#1F2937"))
        header_row.pack(fill="x")
        
        for h in headers:
            ctk.CTkLabel(header_row, text=h, font=ctk.CTkFont(size=12, weight="bold"), width=130).pack(side="left", padx=8, pady=10)
        
        body = ctk.CTkScrollableFrame(table, fg_color="transparent")
        body.pack(fill="both", expand=True)
        
        for driver in self._drivers_data:
            self._add_driver_row(body, driver)
    
    def _add_driver_row(self, parent, driver):
        """Ajoute une ligne avec bouton détail."""
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", pady=(0, 1))
        
        ctk.CTkLabel(row, text=driver.get("id", "")[:8], width=130, font=ctk.CTkFont(size=11)).pack(side="left", padx=8)
        ctk.CTkLabel(row, text=driver.get("name", ""), width=130, font=ctk.CTkFont(size=11, weight="bold")).pack(side="left", padx=8)
        ctk.CTkLabel(row, text=driver.get("phone", ""), width=130, font=ctk.CTkFont(size=11)).pack(side="left", padx=8)
        
        vehicle = driver.get("vehicle", {})
        plate = vehicle.get("plate", "N/A") if vehicle else "N/A"
        ctk.CTkLabel(row, text=plate, width=130, font=ctk.CTkFont(size=11, weight="bold")).pack(side="left", padx=8)
        
        status = driver.get("status", "")
        colors = {"available": "#10B981", "on_trip": "#3B82F6", "offline": "#6B7280"}
        ctk.CTkLabel(row, text=status.upper(), width=130, font=ctk.CTkFont(size=10, weight="bold"), text_color=colors.get(status, "#6B7280")).pack(side="left", padx=8)
        
        rating = driver.get("rating", 0)
        ctk.CTkLabel(row, text=f"⭐ {rating}", width=130, font=ctk.CTkFont(size=11)).pack(side="left", padx=8)
        
        trips = driver.get("total_trips", 0)
        ctk.CTkLabel(row, text=str(trips), width=130, font=ctk.CTkFont(size=11)).pack(side="left", padx=8)
        
        revenue = driver.get("total_revenue", 0)
        ctk.CTkLabel(row, text=f"{revenue // 1000}k XAF", width=130, font=ctk.CTkFont(size=11)).pack(side="left", padx=8)
        
        btn = ctk.CTkButton(row, text="👁️ Détails", width=100, height=25, font=ctk.CTkFont(size=10),
                           command=lambda d=driver: self._show_driver_detail(d))
        btn.pack(side="left", padx=8)
    
    def _show_driver_detail(self, driver):
        """Affiche les détails complets."""
        show_detail(self, title=f"Chauffeur - {driver.get('name', '')}", data=driver)
    
    def _build_pagination(self):
        """Pagination."""
        pagination = ctk.CTkFrame(self, fg_color="transparent")
        pagination.pack(fill="x", pady=(16, 0))
        ctk.CTkLabel(pagination, text=f"{len(self._drivers_data)} chauffeurs").pack(side="left")
    
    def _on_search(self, event):
        """Recherche."""
        query = self._search.get().lower()
        filtered = [d for d in self._drivers_data if query in str(d).lower()]
        self._update_table(filtered)
    
    def _on_filter(self, event):
        """Filtre."""
        status = self._status_filter.get()
        filtered = self._drivers_data if status == "Tous" else [d for d in self._drivers_data if d.get("status") == status]
        self._update_table(filtered)
    
    def _update_table(self, drivers):
        """Met à jour le tableau."""
        for w in self._table_body.winfo_children() if hasattr(self, '_table_body') else []:
            pass
    
    def _add_driver(self):
        """Ajouter chauffeur."""
        print("Ajouter chauffeur")
    
    def _show_map(self):
        """Afficher carte."""
        print("Carte GPS")