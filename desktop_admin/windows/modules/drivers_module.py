# ============================================================
# Module Conducteurs — Gestion des drivers MobiTranz
# Fichier : desktop_admin/windows/modules/drivers_module.py
# Description : Gestion complète des conducteurs avec KYC
# ============================================================

import customtkinter as ctk
from datetime import datetime
from desktop_admin.theme.components import FluentCard, FluentButton, FluentEntry


class DriversModule(ctk.CTkFrame):
    """Module de gestion des conductors.
    
    Fonctions :
    - Liste des conducteurs avec statut KYC
    - Validation des documents
    - Gestion de la disponibilité
    - Statistiques de performance
    """
    
    def __init__(self, master, dashboard=None, user_data=None, **kwargs):
        kwargs.setdefault("fg_color", "transparent")
        super().__init__(master, **kwargs)
        
        self._dashboard = dashboard
        self._user_data = user_data or {}
        self._drivers_data = self._generate_mock_drivers()
        
        self._build_header()
        self._build_stats()
        self._build_filters()
        self._build_table()
    
    def _generate_mock_drivers(self):
        """Génère des données factices."""
        statuses = ["pending", "validated", "suspended"]
        
        drivers = []
        for i in range(30):
            drivers.append({
                "id": f"driver_{i:04d}",
                "user_id": f"user_{i:04d}",
                "phone": f"+24107{i:06d}",
                "first_name": ["Jean", "Marie", "Paul", "Pierre", "Ali"][i % 5],
                "last_name": ["Dupont", "Martin", "Bernard", "Okoué", "Ngoma"][i % 5],
                "license_number": f"LP{i:06d}",
                "status": statuses[i % 3],
                "kyc_verified": i % 3 == 1,
                "rating": round(4.0 + random.random(), 1),
                "total_trips": random.randint(50, 500),
                "total_earnings": random.randint(500000, 5000000),
                "is_available": i % 2 == 0,
                "vehicle": f"Toyota-{['Corolla', 'Hilux', 'Rav4', 'Yaris'][i % 4]}",
                "plate": f"T{i:04d}G",
            })
        return drivers
    
    def _build_header(self):
        """En-tête."""
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(0, 16))
        
        ctk.CTkLabel(
            header,
            text="Gestion des conducteurs",
            font=ctk.CTkFont(family="Segoe UI Variable Display", size=24, weight="bold"),
            text_color=("#1A1A1A", "white"),
        ).pack(side="left")
    
    def _build_stats(self):
        """Cartes de statistiques."""
        stats = ctk.CTkFrame(self, fg_color="transparent")
        stats.pack(fill="x", pady=(0, 16))
        
        stat_items = [
            ("total", "30", "Total drivers", "#1A3A6C"),
            ("validated", "18", "Validés", "#009E60"),
            ("pending", "8", "En attente", "#FCD116"),
            ("suspended", "4", "Suspendus", "#E53E3E"),
        ]
        
        for key, value, label, color in stat_items:
            card = FluentCard(stats, padding=16)
            card.pack(side="left", padx=(0, 12), fill="both", expand=True)
            
            ctk.CTkLabel(
                card,
                text=value,
                font=ctk.CTkFont(family="Segoe UI Variable Display", size=32, weight="bold"),
                text_color=("#1A1A1A", "white"),
            ).pack()
            
            ctk.CTkLabel(
                card,
                text=label,
                font=ctk.CTkFont(size=12),
                text_color=("#6B7280", "#9CA3AF"),
            ).pack()
    
    def _build_filters(self):
        """Filtres de recherche."""
        filters = FluentCard(self, padding=16)
        filters.pack(fill="x", pady=(0, 16))
        
        self._search_entry = FluentEntry(
            filters,
            label="Rechercher",
            placeholder="Nom, téléphone, plaque...",
            width=250
        )
        self._search_entry.pack(side="left", padx=(0, 16))
        
        FluentButton(
            filters,
            text="Rechercher",
            variant="secondary",
            command=self._apply_filters
        ).pack(side="right")
    
    def _build_table(self):
        """Tableau des conducteurs."""
        table_card = FluentCard(self, padding=0)
        table_card.pack(fill="both", expand=True)
        
        headers = ["Driver", "Téléphone", "Véhicule", "Permis", "Note", "Trajets", "Revenus", "Statut", "Actions"]
        
        header_frame = ctk.CTkFrame(table_card, fg_color=("#F5F5F5", "#2C2C2C"), corner_radius=0)
        header_frame.pack(fill="x")
        
        for header in headers:
            width = 100 if header == "Actions" else 120
            ctk.CTkLabel(
                header_frame,
                text=header,
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=("#6B7280", "#9CA3AF"),
                width=width,
            ).pack(side="left", padx=8, pady=12)
        
        self._table_body = ctk.CTkScrollableFrame(
            table_card,
            fg_color="transparent",
        )
        self._table_body.pack(fill="both", expand=True)
        
        self._refresh_table()
    
    def _refresh_table(self, drivers=None):
        """Rafraîchit le tableau."""
        for widget in self._table_body.winfo_children():
            widget.destroy()
        
        drivers = drivers or self._drivers_data
        
        for driver in drivers:
            row = ctk.CTkFrame(self._table_body, fg_color="transparent")
            row.pack(fill="x")
            
            name = f"{driver['first_name']} {driver['last_name']}"
            
            ctk.CTkLabel(
                row,
                text=name,
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=("#1A1A1A", "white"),
                width=120,
            ).pack(side="left", padx=8, pady=8)
            
            ctk.CTkLabel(
                row,
                text=driver["phone"],
                font=ctk.CTkFont(size=11),
                text_color=("#6B7280", "#9CA3AF"),
                width=120,
            ).pack(side="left", padx=8)
            
            ctk.CTkLabel(
                row,
                text=f"🚗 {driver['vehicle']}\n{driver['plate']}",
                font=ctk.CTkFont(size=10),
                text_color=("#6B7280", "#9CA3AF"),
                width=120,
            ).pack(side="left", padx=8)
            
            ctk.CTkLabel(
                row,
                text=driver["license_number"],
                font=ctk.CTkFont(size=11),
                text_color=("#6B7280", "#9CA3AF"),
                width=120,
            ).pack(side="left", padx=8)
            
            rating_color = "#009E60" if driver["rating"] >= 4.5 else "#FCD116"
            ctk.CTkLabel(
                row,
                text=f"⭐ {driver['rating']}",
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color=rating_color,
                width=80,
            ).pack(side="left", padx=8)
            
            ctk.CTkLabel(
                row,
                text=str(driver["total_trips"]),
                font=ctk.CTkFont(size=11),
                text_color=("#6B7280", "#9CA3AF"),
                width=80,
            ).pack(side="left", padx=8)
            
            revenue = f"{driver['total_earnings'] // 1000}k"
            ctk.CTkLabel(
                row,
                text=f"{revenue} XAF",
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color="#009E60",
                width=100,
            ).pack(side="left", padx=8)
            
            status_colors = {
                "validated": ("#009E60", "white"),
                "pending": ("#FCD116", "#1A1A1A"),
                "suspended": ("#E53E3E", "white"),
            }
            s_bg, s_fg = status_colors.get(driver["status"], ("#6B7280", "white"))
            ctk.CTkLabel(
                row,
                text=driver["status"].upper(),
                font=ctk.CTkFont(size=10, weight="bold"),
                text_color=s_fg,
                fg_color=s_bg,
                corner_radius=4,
                padx=8, pady=2
            ).pack(side="left", padx=8)
            
            actions = ctk.CTkFrame(row, fg_color="transparent", width=100)
            actions.pack(side="left", padx=8)
            
            if driver["status"] == "pending":
                FluentButton(
                    actions,
                    text="Valider",
                    variant="success",
                    width=80, height=28,
                    font=ctk.CTkFont(size=10),
                    command=lambda d=driver: self._validate_driver(d)
                ).pack(side="left", padx=2)
            elif driver["status"] == "validated":
                FluentButton(
                    actions,
                    text="Suspendre",
                    variant="danger",
                    width=80, height=28,
                    font=ctk.CTkFont(size=10),
                    command=lambda d=driver: self._suspend_driver(d)
                ).pack(side="left", padx=2)
    
    def _apply_filters(self):
        """Applique les filtres."""
        search = self._search_entry.get().lower()
        
        if search:
            filtered = [d for d in self._drivers_data if 
                        search in d["phone"] or search in d["first_name"].lower() or
                        search in d["plate"].lower()]
            self._refresh_table(filtered)
        else:
            self._refresh_table()
    
    def _validate_driver(self, driver):
        """Valide un driver."""
        driver["status"] = "validated"
        driver["kyc_verified"] = True
        self._refresh_table()
    
    def _suspend_driver(self, driver):
        """Suspend un driver."""
        driver["status"] = "suspended"
        self._refresh_table()


import random