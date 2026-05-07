# ============================================================
# Module Vehicles — Administration
# Fichier : desktop_admin/windows/modules/vehicles_module.py
# ============================================================

import customtkinter as ctk
from desktop_admin.theme.components import FluentCard, KPICard


class VehiclesModule(ctk.CTkFrame):
    """Module de gestion des véhicules."""
    
    def __init__(self, master, user_data=None, dashboard=None, **kwargs):
        kwargs.setdefault("fg_color", "transparent")
        kwargs.pop("dashboard", None)
        kwargs.pop("user_data", None)
        super().__init__(master, **kwargs)
        
        self._dashboard = dashboard
        self._user_data = user_data
        self._current_filter = "all"
        self._sort_column = None
        self._sort_asc = True
        self._detail_drawer = None
        
        self._vehicle_data = [
            {"plate": "AA-001-AI", "brand": "Toyota", "model": "Prius", "places": 4, "status": "ACTIF", "owner": "John Doe", "insurance": "AXA Gabon", "camera": True, "qr": "📱"},
            {"plate": "AA-002-BK", "brand": "Hyundai", "model": "Accent", "places": 4, "status": "ENTRETIEN", "owner": "Marie Ondo", "insurance": "SAAR", "camera": False, "qr": "📱"},
            {"plate": "AA-003-CT", "brand": "Toyota", "model": "Corolla", "places": 5, "status": "ACTIF", "owner": "Pierre Nkog", "insurance": "AXA Gabon", "camera": True, "qr": "📱"},
            {"plate": "AA-004-DL", "brand": "Kia", "model": "Sportage", "places": 5, "status": "ACTIF", "owner": "Paulette M.", "insurance": "SAAR", "camera": True, "qr": "📱"},
            {"plate": "AA-005-EM", "brand": "Nissan", "model": "Altima", "places": 5, "status": "MAINTENANCE", "owner": "Jean B.", "insurance": "AXA Gabon", "camera": False, "qr": "📱"},
        ]
        
        self._build_header()
        self._build_kpis()
        self._build_content()
    
    def _build_header(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(0, 16))
        ctk.CTkLabel(header, text="Gestion des véhicules",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=("#1A1A1A", "white")).pack(side="left")
    
    def _build_kpis(self):
        kpi_frame = ctk.CTkFrame(self, fg_color="transparent")
        kpi_frame.pack(fill="x", pady=(0, 16))
        for i in range(4):
            kpi_frame.grid_columnconfigure(i, weight=1, uniform="kpi")
        
        kpis = [
            ("🚕", "Total", "156", "all"),
            ("✅", "Actifs", "142", "active"),
            ("🔧", "Entretien", "8", "maintenance"),
            ("📹", "Caméra", "98", "with_camera"),
        ]
        
        for i, (icon, title, value, filter_key) in enumerate(kpis):
            kpi_card = KPICard(kpi_frame, icon=icon, title=title, value=value)
            kpi_card.grid(row=0, column=i, sticky="ew", padx=(0, 12 if i < 3 else 0))
            kpi_card.bind("<Button-1>", lambda e, f=filter_key, t=title: self._on_kpi_click(f, t))
            kpi_card.bind("<Enter>", lambda e, w=kpi_card: self._on_hover_enter(e, w))
            kpi_card.bind("<Leave>", lambda e, w=kpi_card: self._on_hover_leave(e, w))
        
        voir_plus_btn = ctk.CTkButton(
            kpi_frame,
            text="Voir plus →",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#1A3A6C",
            hover_color="#2A4A7C",
            width=100,
            height=32,
            command=self._on_voir_plus,
        )
        voir_plus_btn.grid(row=1, column=0, columnspan=4, sticky="e", pady=(12, 0))
    
    def _on_hover_enter(self, event, widget):
        widget.configure(cursor="hand2")
    
    def _on_hover_leave(self, event, widget):
        widget.configure(cursor="")
    
    def _on_kpi_click(self, filter_key, title):
        self._current_filter = filter_key
        self._refresh_list()
        if self._dashboard:
            self._dashboard._topbar_title.configure(text=f"Véhicules - {title}")
    
    def _on_voir_plus(self):
        if self._dashboard:
            self._dashboard._on_nav_click("Véhicules", "vehicles")
    
    def _build_content(self):
        self._card = FluentCard(self, title="Liste des véhicules")
        self._card.pack(fill="both", expand=True)
        content = ctk.CTkFrame(self._card, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        headers = [("Plaque", "plate"), ("Marque", "brand"), ("Modèle", "model"), ("Places", "places"), ("Statut", "status"), ("QR", "qr")]
        self._header_frame = ctk.CTkFrame(content, fg_color=("#F3F4F6", "#2D3748"))
        self._header_frame.pack(fill="x", pady=(0, 8))
        
        for h, col_key in headers:
            header_btn = ctk.CTkButton(
                self._header_frame,
                text=h,
                font=ctk.CTkFont(size=12, weight="bold"),
                fg_color="transparent",
                hover_color=("#E5E7EB", "#3D4858"),
                text_color=("#6B7280", "#9CA3AF"),
                border_width=0,
                command=lambda c=col_key: self._on_sort(c),
            )
            header_btn.pack(side="left", padx=16, pady=8)
        
        self._list_frame = ctk.CTkFrame(content, fg_color="transparent")
        self._list_frame.pack(fill="both", expand=True)
        
        self._refresh_list()
    
    def _on_sort(self, column):
        if self._sort_column == column:
            self._sort_asc = not self._sort_asc
        else:
            self._sort_column = column
            self._sort_asc = True
        self._refresh_list()
    
    def _filter_vehicles(self):
        filtered = self._vehicle_data
        if self._current_filter == "active":
            filtered = [v for v in filtered if v["status"] == "ACTIF"]
        elif self._current_filter == "maintenance":
            filtered = [v for v in filtered if v["status"] == "ENTRETIEN" or v["status"] == "MAINTENANCE"]
        elif self._current_filter == "with_camera":
            filtered = [v for v in filtered if v["camera"]]
        return filtered
    
    def _sort_vehicles(self, vehicles):
        if not self._sort_column:
            return vehicles
        reverse = not self._sort_asc
        return sorted(vehicles, key=lambda v: v.get(self._sort_column, ""), reverse=reverse)
    
    def _refresh_list(self):
        for widget in self._list_frame.winfo_children():
            widget.destroy()
        
        filtered = self._filter_vehicles()
        sorted_vehicles = self._sort_vehicles(filtered)
        
        for v in sorted_vehicles:
            row = ctk.CTkFrame(self._list_frame, fg_color=("white", "#2C2C2C"), corner_radius=8)
            row.pack(fill="x", pady=2)
            row.bind("<Button-1>", lambda e, vehicle=v: self._show_detail_drawer(vehicle))
            row.bind("<Enter>", lambda e, w=row: self._on_row_hover_enter(e, w))
            row.bind("<Leave>", lambda e, w=row: self._on_row_hover_leave(e, w))
            
            cells = [v["plate"], v["brand"], v["model"], str(v["places"]), v["status"], v["qr"]]
            for cell in cells:
                ctk.CTkLabel(row, text=cell, font=ctk.CTkFont(size=12),
                    text_color=("#374151", "#D1D5DB")).pack(side="left", padx=16, pady=10)
    
    def _on_row_hover_enter(self, event, widget):
        widget.configure(cursor="hand2", fg_color=("#E5E7EB", "#3D3D3D"))
    
    def _on_row_hover_leave(self, event, widget):
        widget.configure(cursor="", fg_color=("white", "#2C2C2C"))
    
    def _show_detail_drawer(self, vehicle):
        if self._detail_drawer and self._detail_drawer.winfo_exists():
            self._detail_drawer.destroy()
        
        self._detail_drawer = ctk.CTkToplevel(self)
        self._detail_drawer.title(f"{vehicle['plate']} - Détails")
        self._detail_drawer.geometry("400x500")
        self._detail_drawer.resizable(False, True)
        
        drawer_frame = ctk.CTkFrame(self._detail_drawer, fg_color=("#F9FAFB", "#1F2937"))
        drawer_frame.pack(fill="both", expand=True, padx=16, pady=16)
        
        ctk.CTkLabel(
            drawer_frame,
            text=f"Véhicule: {vehicle['plate']}",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=("#1A1A1A", "white"),
        ).pack(pady=(0, 16))
        
        details = [
            ("Plaque", vehicle["plate"]),
            ("Marque", f"{vehicle['brand']} {vehicle['model']}"),
            ("Owner", vehicle["owner"]),
            ("Insurance", vehicle["insurance"]),
            ("Camera", "✅ Activée" if vehicle["camera"] else "❌ Non activée"),
            ("Status", vehicle["status"]),
            ("Places", str(vehicle["places"])),
        ]
        
        for label, value in details:
            row = ctk.CTkFrame(drawer_frame, fg_color="transparent")
            row.pack(fill="x", pady=4)
            ctk.CTkLabel(
                row,
                text=label,
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=("#6B7280", "#9CA3AF"),
                width=100,
                anchor="w",
            ).pack(side="left")
            ctk.CTkLabel(
                row,
                text=value,
                font=ctk.CTkFont(size=12),
                text_color=("#1A1A1A", "white"),
                anchor="w",
            ).pack(side="left")
        
        ctk.CTkLabel(
            drawer_frame,
            text="Trip History",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=("#1A1A1A", "white"),
            anchor="w",
        ).pack(pady=(16, 8), anchor="w")
        
        trips = [
            ("2024-04-20", "PK12 - PK8", "1500 XAF"),
            ("2024-04-19", "PK12 - PK5", "2000 XAF"),
            ("2024-04-18", "PK8 - PK12", "1800 XAF"),
        ]
        
        for date, route, amount in trips:
            trip_row = ctk.CTkFrame(drawer_frame, fg_color=("white", "#2C2C2C"), corner_radius=6)
            trip_row.pack(fill="x", pady=2)
            ctk.CTkLabel(
                trip_row,
                text=date,
                font=ctk.CTkFont(size=11),
                text_color=("#374151", "#D1D5DB"),
                width=80,
            ).pack(side="left", padx=8, pady=8)
            ctk.CTkLabel(
                trip_row,
                text=route,
                font=ctk.CTkFont(size=11),
                text_color=("#374151", "#D1D5DB"),
            ).pack(side="left", padx=8, pady=8)
            ctk.CTkLabel(
                trip_row,
                text=amount,
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color=("#1A3A6C", "#5B8DEF"),
            ).pack(side="right", padx=8, pady=8)
        
        ctk.CTkLabel(
            drawer_frame,
            text="QR Code",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=("#1A1A1A", "white"),
            anchor="w",
        ).pack(pady=(16, 8), anchor="w")
        
        qr_frame = ctk.CTkFrame(drawer_frame, fg_color=("white", "#2C2C2C"), corner_radius=8)
        qr_frame.pack(fill="x", pady=8)
        ctk.CTkLabel(
            qr_frame,
            text=f"📱 {vehicle['plate']}",
            font=ctk.CTkFont(size=24),
        ).pack(pady=16)
        
        close_btn = ctk.CTkButton(
            drawer_frame,
            text="Fermer",
            fg_color="#6B7280",
            hover_color="#4B5563",
            command=self._detail_drawer.destroy,
        )
        close_btn.pack(pady=(16, 0))