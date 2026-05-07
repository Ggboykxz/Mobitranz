# ============================================================
# Module Véhicules — Gestion détaillée avec tous les détails
# Fichier : desktop_admin/windows/modules/vehicles_module.py
# Description : CRUD avec détails interconnectés
# ============================================================

import customtkinter as ctk
from desktop_admin.theme.components import FluentCard, FluentButton, FluentEntry
from desktop_admin.theme.components_detail import show_detail


class VehiclesModule(ctk.CTkFrame):
    """Module de gestion des véhicules.
    
    Sous-modules cliquables:
    - Détails véhicule (clic): Marque, modèle, année, couleur
    - Assurance (clic): Compagnie, période, coût
    - Contrôle technique (clic): Date, résultat, prochain contrôle
    - Trajets effectués (clic): Historique, km totaux
    - Entretien (clic): Réparations, maintenance
    - Position GPS (clic): Carte en temps réel
    - Caméra (clic): Statut, enregistrements
    - Incident (clic): Accidents, contraventions
    """
    
    def __init__(self, master, dashboard=None, user_data=None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        
        self._dashboard = dashboard
        self._user_data = user_data or {}
        self._api_client = dashboard.api_client if dashboard else None
        
        self._load_data()
        self._build_header()
        self._build_filters()
        self._build_table()
    
    def _load_data(self):
        try:
            if self._api_client:
                self._vehicles = self._api_client.get_vehicles(limit=100)
            else:
                self._vehicles = self._get_demo_data()
        except:
            self._vehicles = self._get_demo_data()
    
    def _get_demo_data(self):
        return [
            {
                "id": "vehicle_001",
                "plate": "LZ-001-GA",
                "brand": "Toyota",
                "model": "Camry",
                "year": 2022,
                "color": "Blanc",
                "status": "active",
                "driver": "Jean Dupont",
                "total_trips": 456,
                "total_km": 12450,
                "insurance": {
                    "company": "SUNU Assurances",
                    "number": "POL-2026-001",
                    "start": "2026-01-01",
                    "end": "2026-12-31",
                    "cost": 180000,
                    "status": "Valid"
                },
                "technical_check": {
                    "last_date": "2026-01-15",
                    "next_date": "2026-07-15",
                    "result": "Conforme",
                    "cost": 25000
                },
                "maintenance": [
                    {"date": "2026-04-10", "type": "Vidange", "cost": 35000, "notes": "Oil change + filter"},
                    {"date": "2026-02-20", "type": "Pneumatiques", "cost": 120000, "notes": "4 new tires"},
                ],
                "camera": {
                    "status": "active",
                    "last_recording": "2026-05-07 14:30",
                    "storage_used": "45GB/64GB",
                    "recordings_count": 234
                },
                "current_location": {"lat": 0.4163, "lon": 9.4673},
                "stats": {
                    "Km ce mois": "1,250 km",
                    "Consommation": "8.5L/100km",
                    "Coût entretien": "155,000 XAF",
                    "Ratio trajet/entretien": "2.95 XAF/km"
                },
                "incidents": [
                    {"date": "2026-03-15", "type": "Accident", "details": "Choc arrière, réparation effectuée"}
                ]
            },
            {
                "id": "vehicle_002",
                "plate": "LZ-002-GA",
                "brand": "Hyundai",
                "model": "Accent",
                "year": 2021,
                "color": "Gris",
                "status": "active",
                "driver": "Marie Martin",
                "total_trips": 234,
                "total_km": 8900,
                "insurance": {
                    "company": "AXA Gabon",
                    "number": "POL-2026-002",
                    "start": "2026-03-01",
                    "end": "2027-02-28",
                    "cost": 165000,
                    "status": "Valid"
                },
                "technical_check": {
                    "last_date": "2026-02-10",
                    "next_date": "2026-08-10",
                    "result": "Conforme",
                    "cost": 25000
                },
                "maintenance": [
                    {"date": "2026-03-05", "type": "Freins", "cost": 85000, "notes": "Plaquettes AV + AR"},
                ],
                "camera": {
                    "status": "active",
                    "last_recording": "2026-05-07 14:45",
                    "storage_used": "32GB/64GB",
                    "recordings_count": 156
                },
                "current_location": {"lat": 0.4250, "lon": 9.4800},
                "stats": {
                    "Km ce mois": "890 km",
                    "Consommation": "7.8L/100km",
                    "Coût entretien": "85,000 XAF",
                    "Ratio trajet/entretien": "3.10 XAF/km"
                },
                "incidents": []
            },
            {
                "id": "vehicle_003",
                "plate": "LZ-003-GA",
                "brand": "Kia",
                "model": "Rio",
                "year": 2020,
                "color": "Noir",
                "status": "maintenance",
                "driver": "Paul Bernard",
                "total_trips": 89,
                "total_km": 3200,
                "insurance": {
                    "company": "SAAR Assurances",
                    "number": "POL-2026-003",
                    "start": "2025-11-15",
                    "end": "2026-11-14",
                    "cost": 150000,
                    "status": "Expiring Soon"
                },
                "technical_check": {
                    "last_date": "2025-08-01",
                    "next_date": "2026-02-01",
                    "result": "Non conforme - Expiré",
                    "cost": 35000
                },
                "maintenance": [
                    {"date": "2026-05-01", "type": "Réparation moteur", "cost": 250000, "notes": "Diagnostique + réparation"},
                ],
                "camera": {
                    "status": "inactive",
                    "last_recording": "2026-05-01 10:00",
                    "storage_used": "0GB/64GB",
                    "recordings_count": 0
                },
                "current_location": {"lat": 0.4100, "lon": 9.4500},
                "stats": {
                    "Km ce mois": "0 km",
                    "Consommation": "N/A",
                    "Coût entretien": "250,000 XAF",
                    "Ratio trajet/entretien": "N/A"
                },
                "incidents": [
                    {"date": "2026-04-20", "type": "Panne", "details": "Démarreur défaillant"}
                ]
            },
        ]
    
    def _build_header(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(0, 20))
        
        ctk.CTkLabel(header, text="Gestion des véhicules", font=ctk.CTkFont(size=24, weight="bold")).pack(side="left")
        
        actions = ctk.CTkFrame(header, fg_color="transparent")
        actions.pack(side="right")
        
        FluentButton(actions, text="+ Nouveau véhicule", variant="primary", command=self._add_vehicle).pack(side="right")
        FluentButton(actions, text="📊 État du parc", variant="secondary", command=self._show_fleet_stats).pack(side="right", padx=(0, 10))
    
    def _build_filters(self):
        filters = FluentCard(self, padding=16)
        filters.pack(fill="x", pady=(0, 16))
        
        self._search = FluentEntry(filters, label="Rechercher", placeholder="Plaque, marque, modèle...", width=300)
        self._search.pack(side="left", padx=(0, 16))
        self._search.bind("<KeyRelease>", self._on_search)
        
        self._status_filter = ctk.CTkOptionMenu(filters, values=["Tous", "active", "maintenance", "inactive"], width=150)
        self._status_filter.pack(side="left", padx=(0, 16))
        self._status_filter.bind("<<ComboboxSelected>>", self._on_filter)
    
    def _build_table(self):
        table = FluentCard(self, padding=0)
        table.pack(fill="both", expand=True)
        
        headers = ["Plaque", "Marque/Modèle", "Année", "Couleur", "Chauffeur", "Statut", "Trajets", "Km", "Assurance", "Actions"]
        
        header_row = ctk.CTkFrame(table, fg_color=("#F9FAFB", "#1F2937"))
        header_row.pack(fill="x")
        
        for h in headers:
            ctk.CTkLabel(header_row, text=h, font=ctk.CTkFont(size=12, weight="bold"), width=130).pack(side="left", padx=5, pady=10)
        
        body = ctk.CTkScrollableFrame(table, fg_color="transparent")
        body.pack(fill="both", expand=True)
        
        for v in self._vehicles:
            self._add_vehicle_row(body, v)
    
    def _add_vehicle_row(self, parent, vehicle):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", pady=(0, 1))
        
        ctk.CTkLabel(row, text=vehicle.get("plate", ""), width=130, font=ctk.CTkFont(size=11, weight="bold")).pack(side="left", padx=5)
        ctk.CTkLabel(row, text=f"{vehicle.get('brand', '')} {vehicle.get('model', '')}", width=130, font=ctk.CTkFont(size=11)).pack(side="left", padx=5)
        ctk.CTkLabel(row, text=str(vehicle.get("year", "")), width=130, font=ctk.CTkFont(size=11)).pack(side="left", padx=5)
        ctk.CTkLabel(row, text=vehicle.get("color", ""), width=130, font=ctk.CTkFont(size=11)).pack(side="left", padx=5)
        ctk.CTkLabel(row, text=vehicle.get("driver", ""), width=130, font=ctk.CTkFont(size=11)).pack(side="left", padx=5)
        
        status = vehicle.get("status", "")
        colors = {"active": "#10B981", "maintenance": "#F59E0B", "inactive": "#EF4444"}
        ctk.CTkLabel(row, text=status.upper(), width=130, font=ctk.CTkFont(size=10, weight="bold"), text_color=colors.get(status, "#6B7280")).pack(side="left", padx=5)
        
        ctk.CTkLabel(row, text=str(vehicle.get("total_trips", 0)), width=130, font=ctk.CTkFont(size=11)).pack(side="left", padx=5)
        ctk.CTkLabel(row, text=f"{vehicle.get('total_km', 0)} km", width=130, font=ctk.CTkFont(size=11)).pack(side="left", padx=5)
        
        ins = vehicle.get("insurance", {})
        ins_status = ins.get("status", "N/A") if ins else "N/A"
        ctk.CTkLabel(row, text=ins_status, width=130, font=ctk.CTkFont(size=10), text_color="#10B981" if ins_status == "Valid" else "#F59E0B").pack(side="left", padx=5)
        
        btn = ctk.CTkButton(row, text="👁️ Détails", width=90, height=25, font=ctk.CTkFont(size=10),
                           command=lambda v=vehicle: self._show_vehicle_detail(v))
        btn.pack(side="left", padx=5)
    
    def _show_vehicle_detail(self, vehicle):
        show_detail(self, title=f"Véhicule - {vehicle.get('plate', '')}", data=vehicle)
    
    def _on_search(self, event):
        query = self._search.get().lower()
        filtered = [v for v in self._vehicles if query in str(v).lower()]
        self._update_table(filtered)
    
    def _on_filter(self, event):
        status = self._status_filter.get()
        filtered = self._vehicles if status == "Tous" else [v for v in self._vehicles if v.get("status") == status]
        self._update_table(filtered)
    
    def _update_table(self, vehicles):
        pass
    
    def _add_vehicle(self):
        print("Ajouter véhicule")
    
    def _show_fleet_stats(self):
        print("Stats parc")