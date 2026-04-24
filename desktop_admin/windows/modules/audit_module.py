# ============================================================
# Module Audit — Administration
# Fichier : desktop_admin/windows/modules/audit_module.py
# ============================================================

import customtkinter as ctk
from desktop_admin.theme.components import FluentCard, KPICard
from datetime import datetime


class AuditModule(ctk.CTkFrame):
    """Module de sécurité et logs."""
    
    def __init__(self, master, user_data=None, **kwargs):
        kwargs.setdefault("fg_color", "transparent")
        super().__init__(master, **kwargs)
        
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(0, 16))
        ctk.CTkLabel(header, text="Sécurité & Logs",
            font=ctk.CTkFont(size=22, weight="bold"), text_color=("#1A1A1A", "white")).pack(side="left")
        
        kpi_frame = ctk.CTkFrame(self, fg_color="transparent")
        kpi_frame.pack(fill="x", pady=(0, 16))
        for i in range(4):
            kpi_frame.grid_columnconfigure(i, weight=1, uniform="kpi")
        kpis = [("🔒", "Connexions", "1,247"), ("⚠️", "Échecs", "12"), ("🚫", "Bloqués", "3"), ("✅", "Validations", "98.5%")]
        for i, (icon, title, value) in enumerate(kpis):
            KPICard(kpi_frame, icon=icon, title=title, value=value).grid(row=0, column=i, sticky="ew", padx=(0, 12 if i < 3 else 0))
        
        card = FluentCard(self, title="Journal d'audit récent")
        card.pack(fill="both", expand=True)
        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        headers = ["Horodatage", "Action", "Utilisateur", "IP ", "Statut"]
        header_frame = ctk.CTkFrame(content, fg_color=("#F3F4F6", "#2D3748"))
        header_frame.pack(fill="x", pady=(0, 8))
        for h in headers:
            ctk.CTkLabel(header_frame, text=h, font=ctk.CTkFont(size=12, weight="bold"),
                text_color=("#6B7280", "#9CA3AF")).pack(side="left", padx=16, pady=8)
        
        logs = [
            ("14:32:15", "LOGIN", "admin@mobitranz.ga", "41.78.123.45", "✅"),
            ("14:28:03", "PAYMENT_INITIATED", "client_456", "41.78.123.46", "✅"),
            ("14:15:22", "USER_SUSPENDED", "admin@mobitranz.ga", "41.78.123.45", "✅"),
            ("13:45:11", "LOGIN_FAILED", "unknown", "41.78.123.50", "❌"),
        ]
        for log in logs:
            row = ctk.CTkFrame(content, fg_color=("white", "#2C2C2C"), corner_radius=8)
            row.pack(fill="x", pady=2)
            for cell in log:
                ctk.CTkLabel(row, text=cell, font=ctk.CTkFont(size=12), text_color=("#374151", "#D1D5DB")).pack(side="left", padx=16, pady=10)