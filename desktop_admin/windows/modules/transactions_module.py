# ============================================================
# Module Transactions — Administration
# Fichier : desktop_admin/windows/modules/transactions_module.py
# ============================================================

import customtkinter as ctk
from desktop_admin.theme.components import FluentCard, KPICard


class TransactionsModule(ctk.CTkFrame):
    """Module de gestion des transactions."""
    
    def __init__(self, master, user_data=None, **kwargs):
        kwargs.setdefault("fg_color", "transparent")
        super().__init__(master, **kwargs)
        
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(0, 16))
        ctk.CTkLabel(header, text="Transactions",
            font=ctk.CTkFont(size=22, weight="bold"), text_color=("#1A1A1A", "white")).pack(side="left")
        
        kpi_frame = ctk.CTkFrame(self, fg_color="transparent")
        kpi_frame.pack(fill="x", pady=(0, 16))
        for i in range(4):
            kpi_frame.grid_columnconfigure(i, weight=1, uniform="kpi")
        kpis = [("💰", "Total", "15.2M"), ("✅", "Réussies", "14.8M"), ("❌", "Échouées", "320K"), ("📊", "Taux", "98.2%")]
        for i, (icon, title, value) in enumerate(kpis):
            KPICard(kpi_frame, icon=icon, title=title, value=value).grid(row=0, column=i, sticky="ew", padx=(0, 12 if i < 3 else 0))
        
        card = FluentCard(self, title="Historique des transactions")
        card.pack(fill="both", expand=True)
        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        headers = ["ID", "Montant", "Méthode", "Statut", "Date"]
        header_frame = ctk.CTkFrame(content, fg_color=("#F3F4F6", "#2D3748"))
        header_frame.pack(fill="x", pady=(0, 8))
        for h in headers:
            ctk.CTkLabel(header_frame, text=h, font=ctk.CTkFont(size=12, weight="bold"),
                text_color=("#6B7280", "#9CA3AF")).pack(side="left", padx=16, pady=8)
        
        for t in [("pay_001", "1,500", "MoovMoney", "✅", "14:32"), ("pay_002", "800", "Airtel", "✅", "14:28"), ("pay_003", "2,000", "Carte", "❌", "14:15")]:
            row = ctk.CTkFrame(content, fg_color=("white", "#2C2C2C"), corner_radius=8)
            row.pack(fill="x", pady=2)
            for cell in t:
                ctk.CTkLabel(row, text=cell, font=ctk.CTkFont(size=12), text_color=("#374151", "#D1D5DB")).pack(side="left", padx=16, pady=10)