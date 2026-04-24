# ============================================================
# Module Recordings — Administration
# Fichier : desktop_admin/windows/modules/recordings_module.py
# ============================================================

import customtkinter as ctk
from desktop_admin.theme.components import FluentCard, KPICard


class RecordingsModule(ctk.CTkFrame):
    """Module de gestion des vidéos."""
    
    def __init__(self, master, user_data=None, **kwargs):
        kwargs.setdefault("fg_color", "transparent")
        super().__init__(master, **kwargs)
        
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(0, 16))
        ctk.CTkLabel(header, text="Enregistrements vidéo",
            font=ctk.CTkFont(size=22, weight="bold"), text_color=("#1A1A1A", "white")).pack(side="left")
        
        kpi_frame = ctk.CTkFrame(self, fg_color="transparent")
        kpi_frame.pack(fill="x", pady=(0, 16))
        for i in range(3):
            kpi_frame.grid_columnconfigure(i, weight=1, uniform="kpi")
        kpis = [("📹", "Enregistrements", "1,247"), ("🔒", "Chiffrés", "1,198"), ("👁️", "Vus (24h)", "12")]
        for i, (icon, title, value) in enumerate(kpis):
            KPICard(kpi_frame, icon=icon, title=title, value=value).grid(row=0, column=i, sticky="ew", padx=(0, 16 if i < 2 else 0))
        
        card = FluentCard(self, title="Derniers enregistrements")
        card.pack(fill="both", expand=True)
        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        headers = ["ID", "Trajet", "Véhicule", "Durée", "Statut", "Actions"]
        header_frame = ctk.CTkFrame(content, fg_color=("#F3F4F6", "#2D3748"))
        header_frame.pack(fill="x", pady=(0, 8))
        for h in headers:
            ctk.CTkLabel(header_frame, text=h, font=ctk.CTkFont(size=12, weight="bold"),
                text_color=("#6B7280", "#9CA3AF")).pack(side="left", padx=16, pady=8)
        
        for r in [("rec_001", "trip_123", "AA-001-AI", "12:34", "CHIFFRÉ", "👁️"), ("rec_002", "trip_124", "AA-002-BK", "08:21", "CHIFFRÉ", "👁️")]:
            row = ctk.CTkFrame(content, fg_color=("white", "#2C2C2C"), corner_radius=8)
            row.pack(fill="x", pady=2)
            for cell in r:
                ctk.CTkLabel(row, text=cell, font=ctk.CTkFont(size=12), text_color=("#374151", "#D1D5DB")).pack(side="left", padx=16, pady=10)