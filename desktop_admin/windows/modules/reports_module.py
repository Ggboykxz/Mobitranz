# ============================================================
# Module Rapports — Génération de rapports MobiTranz
# Fichier : desktop_admin/windows/modules/reports_module.py
# Description : Rapports ministériels et exports PDF/CSV
# ============================================================

import customtkinter as ctk
from datetime import datetime, timedelta
from desktop_admin.theme.components import FluentCard, FluentButton


class ReportsModule(ctk.CTkFrame):
    """Module de génération de rapports."""
    
    def __init__(self, master, dashboard=None, user_data=None, **kwargs):
        kwargs.setdefault("fg_color", "transparent")
        super().__init__(master, **kwargs)
        
        self._build_header()
        self._build_ministry_reports()
        self._build_financial_reports()
        self._build_custom_reports()
    
    def _build_header(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(0, 20))
        
        ctk.CTkLabel(header, text="Rapports et exports",
                    font=ctk.CTkFont(size=24, weight="bold")).pack(side="left")
    
    def _build_ministry_reports(self):
        """Rapports pour les ministères."""
        section = ctk.CTkFrame(self, fg_color="transparent")
        section.pack(fill="x", pady=(0, 16))
        
        ctk.CTkLabel(section, text="📊 Rapports ministériels",
                    font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", pady=(0, 12))
        
        reports = [
            ("🚛", "Ministère des Transports", "Rapport mensuel trafic", "Générer"),
            ("🛡️", "Ministère de l'Intérieur", "Rapport sécurité incidents", "Générer"),
            ("📋", "Direction Générale", "Statistiques globales", "Générer"),
        ]
        
        for icon, title, desc, action in reports:
            card = FluentCard(section, padding=16)
            card.pack(fill="x", pady=(0, 8))
            
            row = ctk.CTkFrame(card, fg_color="transparent")
            row.pack(fill="x")
            
            ctk.CTkLabel(row, text=icon, font=ctk.CTkFont(size=24)).pack(side="left", padx=(0, 12))
            
            info = ctk.CTkFrame(row, fg_color="transparent")
            info.pack(side="left", fill="x", expand=True)
            
            ctk.CTkLabel(info, text=title, font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w")
            ctk.CTkLabel(info, text=desc, font=ctk.CTkFont(size=11), text_color="#6B7280").pack(anchor="w")
            
            FluentButton(row, text=action, variant="primary", command=lambda t=title: self._generate_report(t)).pack(side="right")
    
    def _build_financial_reports(self):
        """Rapports financiers."""
        section = ctk.CTkFrame(self, fg_color="transparent")
        section.pack(fill="x", pady=(0, 16))
        
        ctk.CTkLabel(section, text="💰 Rapports financiers",
                    font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", pady=(0, 12))
        
        grid = ctk.CTkFrame(section, fg_color="transparent")
        grid.pack(fill="x")
        grid.grid_columnconfigure(0, weight=1)
        grid.grid_columnconfigure(1, weight=1)
        
        cards = [
            ("📅", "Rapport journalier", "Détails par jour"),
            ("📆", "Rapport hebdomadaire", "Résumé hebdo"),
            ("🗓️", "Rapport mensuel", "Bilan mensuel"),
            ("📊", "Analyse tendances", "Évolution sur 6 mois"),
        ]
        
        for i, (icon, title, desc) in enumerate(cards):
            card = FluentCard(grid, padding=16)
            card.grid(row=i//2, column=i%2, sticky="nsew", padx=(0, 8), pady=(0, 8))
            
            ctk.CTkLabel(card, text=icon, font=ctk.CTkFont(size=24)).pack()
            ctk.CTkLabel(card, text=title, font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(8, 4))
            ctk.CTkLabel(card, text=desc, font=ctk.CTkFont(size=11), text_color="#6B7280").pack()
            
            btns = ctk.CTkFrame(card, fg_color="transparent")
            btns.pack(pady=(12, 0))
            
            FluentButton(btns, text="📄 PDF", variant="secondary", width=70, height=28,
                        command=lambda t=title: self._export_pdf(t)).pack(side="left", padx=4)
            FluentButton(btns, text="📊 CSV", variant="secondary", width=70, height=28,
                        command=lambda t=title: self._export_csv(t)).pack(side="left", padx=4)
    
    def _build_custom_reports(self):
        """Rapports personnalisés."""
        section = ctk.CTkFrame(self, fg_color="transparent")
        section.pack(fill="both", expand=True)
        
        ctk.CTkLabel(section, text="📈 Rapports personnalisés",
                    font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", pady=(0, 12))
        
        card = FluentCard(section, padding=20)
        card.pack(fill="both", expand=True)
        
        form = ctk.CTkFrame(card, fg_color="transparent")
        form.pack(fill="x")
        
        ctk.CTkLabel(form, text="Type de données:", font=ctk.CTkFont(size=12)).pack(side="left", padx=(0, 8))
        
        data_type = ctk.CTkOptionMenu(form, values=["Trajets", "Transactions", "Utilisateurs", "Drivers", "Incidents"],
                                      width=180)
        data_type.pack(side="left", padx=(0, 16))
        
        ctk.CTkLabel(form, text="Période:", font=ctk.CTkFont(size=12)).pack(side="left", padx=(0, 8))
        
        period = ctk.CTkOptionMenu(form, values=["Aujourd'hui", "7 derniers jours", "30 derniers jours", "Ce mois", "Ce trimestre"],
                                   width=180)
        period.pack(side="left", padx=(0, 16))
        
        FluentButton(form, text="Générer", variant="primary").pack(side="right")
        
        ctk.CTkLabel(card, text="Colonnes à inclure:", font=ctk.CTkFont(size=12), pady=(16, 8)).pack(anchor="w")
        
        cols_frame = ctk.CTkFrame(card, fg_color="transparent")
        cols_frame.pack(fill="x")
        
        cols = ["Date", "ID", "Montant", "Statut", "Client", "Chauffeur", "Origine", "Destination"]
        
        for col in cols:
            ctk.CTkCheckBox(cols_frame, text=col).pack(side="left", padx=8)
    
    def _generate_report(self, title):
        """Génère un rapport."""
        print(f"Génération: {title}")
    
    def _export_pdf(self, title):
        """Exporte en PDF."""
        print(f"Export PDF: {title}")
    
    def _export_csv(self, title):
        """Exporte en CSV."""
        print(f"Export CSV: {title}")