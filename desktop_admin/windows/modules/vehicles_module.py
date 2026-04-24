# ============================================================
# Module Vehicles — Administration
# Fichier : desktop_admin/windows/modules/vehicles_module.py
# ============================================================

import customtkinter as ctk
from desktop_admin.theme.components import FluentCard, KPICard


class VehiclesModule(ctk.CTkFrame):
    """Module de gestion des véhicules."""
    
    def __init__(self, master, user_data=None, **kwargs):
        kwargs.setdefault("fg_color", "transparent")
        super().__init__(master, **kwargs)
        
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
        kpis = [("🚕", "Total", "156"), ("✅", "Actifs", "142"), ("🔧", "Entretien", "8"), ("📹", "Caméra", "98")]
        for i, (icon, title, value) in enumerate(kpis):
            KPICard(kpi_frame, icon=icon, title=title, value=value).grid(row=0, column=i, sticky="ew", padx=(0, 12 if i < 3 else 0))

    def _build_content(self):
        card = FluentCard(self, title="Liste des véhicules")
        card.pack(fill="both", expand=True)
        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        headers = ["Plaque", "Marque", "Modèle", "Places", "Statut", "QR"]
        header_frame = ctk.CTkFrame(content, fg_color=("#F3F4F6", "#2D3748"))
        header_frame.pack(fill="x", pady=(0, 8))
        for h in headers:
            ctk.CTkLabel(header_frame, text=h, font=ctk.CTkFont(size=12, weight="bold"),
                text_color=("#6B7280", "#9CA3AF")).pack(side="left", padx=16, pady=8)

        vehicles = [("AA-001-AI", "Toyota", "Prius", "4", "ACTIF", "📱"), ("AA-002-BK", "Hyundai", "Accent", "4", "ENTRETIEN", "📱")]
        for v in vehicles:
            row = ctk.CTkFrame(content, fg_color=("white", "#2C2C2C"), corner_radius=8)
            row.pack(fill="x", pady=2)
            for cell in v:
                ctk.CTkLabel(row, text=cell, font=ctk.CTkFont(size=12),
                    text_color=("#374151", "#D1D5DB")).pack(side="left", padx=16, pady=10)