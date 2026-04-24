# ============================================================
# Module Incidents — Administration
# Fichier : desktop_admin/windows/modules/incidents_module.py
# ============================================================

import customtkinter as ctk
from desktop_admin.theme.components import FluentCard, KPICard, FluentButton
from datetime import datetime


class IncidentsModule(ctk.CTkFrame):
    """Module de gestion des incidents."""
    
    def __init__(self, master, user_data=None, **kwargs):
        kwargs.setdefault("fg_color", "transparent")
        super().__init__(master, **kwargs)
        
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(0, 16))
        ctk.CTkLabel(header, text="Incidents SOS",
            font=ctk.CTkFont(size=22, weight="bold"), text_color=("#E53E3E", "#FC8181")).pack(side="left")
        
        right = ctk.CTkFrame(header, fg_color="transparent")
        right.pack(side="right")
        ctk.CTkLabel(right, text=f"🕐 {datetime.now().strftime('%H:%M:%S')}",
            font=ctk.CTkFont(size=12), text_color=("#9A9A9A", "#6D6D6D")).pack(side="right")
        
        kpi_frame = ctk.CTkFrame(self, fg_color="transparent")
        kpi_frame.pack(fill="x", pady=(0, 16))
        for i in range(4):
            kpi_frame.grid_columnconfigure(i, weight=1, uniform="kpi")
        kpis = [("🚨", "Total", "23"), ("⏳", "Ouverts", "3"), ("🔄", "En cours", "5"), ("✅", "Résolus", "15")]
        for i, (icon, title, value) in enumerate(kpis):
            KPICard(kpi_frame, icon=icon, title=title, value=value, accent_color="#E53E3E").grid(row=0, column=i, sticky="ew", padx=(0, 12 if i < 3 else 0))
        
        card = FluentCard(self, title="Incidents récents")
        card.pack(fill="both", expand=True)
        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        headers = ["ID", "Type", "Trajet", "Statut", "Signalé à"]
        header_frame = ctk.CTkFrame(content, fg_color=("#FEE2E2", "#4A1A1A"))
        header_frame.pack(fill="x", pady=(0, 8))
        for h in headers:
            ctk.CTkLabel(header_frame, text=h, font=ctk.CTkFont(size=12, weight="bold"),
                text_color=("#991B1B", "#FCA5A5")).pack(side="left", padx=16, pady=8)
        
        incidents = [("inc_001", "🚨 SOS", "trip_123", "OUVERT", "14:32"), ("inc_002", "⚠️ DISPUTE", "trip_124", "EN COURS", "13:45"), ("inc_003", "🚗 ACCIDENT", "trip_125", "RÉSOLU", "hier")]
        for inc in incidents:
            row = ctk.CTkFrame(content, fg_color=("white", "#2C2C2C"), corner_radius=8)
            row.pack(fill="x", pady=2)
            for cell in inc:
                ctk.CTkLabel(row, text=cell, font=ctk.CTkFont(size=12), text_color=("#374151", "#D1D5DB")).pack(side="left", padx=16, pady=10)