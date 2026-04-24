# ============================================================
# Module Reports — Administration
# Fichier : desktop_admin/windows/modules/reports_module.py
# ============================================================

import customtkinter as ctk
from desktop_admin.theme.components import FluentCard, KPICard, FluentButton


class ReportsModule(ctk.CTkFrame):
    """Module de rapports ministériels."""
    
    def __init__(self, master, user_data=None, **kwargs):
        kwargs.setdefault("fg_color", "transparent")
        super().__init__(master, **kwargs)
        
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(0, 16))
        ctk.CTkLabel(header, text="Rapports ministériels",
            font=ctk.CTkFont(size=22, weight="bold"), text_color=("#1A1A1A", "white")).pack(side="left")
        
        right = ctk.CTkFrame(header, fg_color="transparent")
        right.pack(side="right")
        FluentButton(right, text="📥 Exporter CSV", variant="secondary", height=36).pack(side="right")
        
        kpi_frame = ctk.CTkFrame(self, fg_color="transparent")
        kpi_frame.pack(fill="x", pady=(0, 16))
        for i in range(3):
            kpi_frame.grid_columnconfigure(i, weight=1, uniform="kpi")
        kpis = [("📊", "Rapports générés", "24"), ("📅", "Ce mois", "8"), ("📧", "Envoyés", "6")]
        for i, (icon, title, value) in enumerate(kpis):
            KPICard(kpi_frame, icon=icon, title=title, value=value).grid(row=0, column=i, sticky="ew", padx=(0, 16 if i < 2 else 0))
        
        card = FluentCard(self, title="Générer un rapport")
        card.pack(fill="both", expand=False, pady=(0, 16))
        
        form = ctk.CTkFrame(card, fg_color="transparent")
        form.pack(fill="x", padx=20, pady=20)
        
        ctk.CTkLabel(form, text="Période:", font=ctk.CTkFont(size=14),
            text_color=("#374151", "#D1D5DB")).pack(anchor="w", pady=(0, 8))
        
        period_frame = ctk.CTkFrame(form, fg_color="transparent")
        period_frame.pack(fill="x", pady=(0, 16))
        ctk.CTkLabel(period_frame, text="2026-04", font=ctk.CTkFont(size=14, weight="bold"),
            text_color=("#1A1A1A", "white")).pack(side="left")
        
        ctk.CTkLabel(form, text="Type de rapport:", font=ctk.CTkFont(size=14),
            text_color=("#374151", "#D1D5DB")).pack(anchor="w", pady=(0, 8))
        type_frame = ctk.CTkFrame(form, fg_color="transparent")
        type_frame.pack(fill="x", pady=(0, 16))
        
        for t in ["Statistiques globales", "Revenus par zone", "Incidents", "Conformité"]:
            ctk.CTkLabel(type_frame, text=f"• {t}", font=ctk.CTkFont(size=13),
                text_color=("#374151", "#D1D5DB")).pack(anchor="w", pady=2)
        
        FluentButton(form, text="📊 Générer le rapport", variant="primary", height=44).pack(fill="x", pady=(16, 0))