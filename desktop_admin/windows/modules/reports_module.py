# ============================================================
# Module Reports — Administration
# Fichier : desktop_admin/windows/modules/reports_module.py
# ============================================================

import customtkinter as ctk
from desktop_admin.theme.components import FluentCard, KPICard, FluentButton


class ClickableKPICard(KPICard):
    """KPICard cliquable pour navigation vers analytics."""
    
    def __init__(self, master, icon, title, value, navigate_to=None, **kwargs):
        super().__init__(master, icon=icon, title=title, value=value, **kwargs)
        self.navigate_to = navigate_to
        self.bind("<Button-1>", self._on_click)
        self.bind("<Enter>", self._on_hover)
        self.bind("<Leave>", self._on_leave)
        self.configure(cursor="hand2")
    
    def _on_click(self, event):
        if self.navigate_to:
            print(f"Navigation vers: {self.navigate_to}")
    
    def _on_hover(self, event):
        self.configure(cursor="hand2")
    
    def _on_leave(self, event):
        self.configure(cursor="arrow")


class ClickableReportRow(ctk.CTkFrame):
    """Ligne de rapport cliquable."""
    
    def __init__(self, master, report_data, on_click=None, **kwargs):
        kwargs.setdefault("fg_color", ("#F3F4F6", "#1F2937"))
        super().__init__(master, **kwargs)
        self.report_data = report_data
        self.on_click = on_click
        self._hover = False
        
        self.pack(fill="x", pady=2)
        
        self.bind("<Button-1>", self._on_click)
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Motion>", self._on_motion)
        self.configure(cursor="hand2")
        
        self._build_ui()
    
    def _build_ui(self):
        date, report_type, dest, status, records = self.report_data
        status_colors = {
            "Terminé": ("#10B981", "#065F46"),
            "En cours": ("#F59E0B", "#92400E"),
            "En attente": ("#6B7280", "#374151")
        }
        status_fg, status_bg = status_colors.get(status, ("#6B7280", "#374151"))
        
        ctk.CTkLabel(self, text=date, font=ctk.CTkFont(size=13),
            text_color=("#374151", "#D1D5DB"), width=100).pack(side="left", padx=12, pady=12)
        ctk.CTkLabel(self, text=report_type, font=ctk.CTkFont(size=13, weight="bold"),
            text_color=("#1A1A1A", "white"), width=180).pack(side="left", padx=12)
        ctk.CTkLabel(self, text=dest, font=ctk.CTkFont(size=13),
            text_color=("#374151", "#D1D5DB"), width=120).pack(side="left", padx=12)
        ctk.CTkLabel(self, text=status, font=ctk.CTkFont(size=12, weight="bold"),
            text_color=status_fg, fg_color=status_bg, corner_radius=6,
            width=80, height=24).pack(side="left", padx=12)
        ctk.CTkLabel(self, text=f"{records} lignes", font=ctk.CTkFont(size=13),
            text_color=("#374151", "#D1D5DB")).pack(side="right", padx=12)
    
    def _on_click(self, event):
        if self.on_click:
            self.on_click(self.report_data)
        print(f"Ouvrir rapport: {self.report_data}")
    
    def _on_enter(self, event):
        self._hover = True
        self.configure(fg_color=("#E5E7EB", "#374151"))
    
    def _on_leave(self, event):
        self._hover = False
        self.configure(fg_color=("#F3F4F6", "#1F2937"))
    
    def _on_motion(self, event):
        if not self._hover:
            self._on_enter(event)


class ReportsModule(ctk.CTkFrame):
    """Module de rapports ministériels."""
    
    def __init__(self, master, user_data=None, dashboard=None, **kwargs):
        kwargs.setdefault("fg_color", "transparent")
        kwargs.pop("dashboard", None)
        kwargs.pop("user_data", None)
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
        kpis = [
            ("📊", "Rapports générés", "24", "analytics_generated"),
            ("📅", "Ce mois", "8", "analytics_monthly"),
            ("📧", "Envoyés", "6", "analytics_sent")
        ]
        for i, (icon, title, value, nav) in enumerate(kpis):
            ClickableKPICard(kpi_frame, icon=icon, title=title, value=value, navigate_to=nav).grid(
                row=0, column=i, sticky="ew", padx=(0, 16 if i < 2 else 0))
        
        card = FluentCard(self, title="Générer un rapport")
        card.pack(fill="both", expand=False, pady=(0, 16))
        
        form = ctk.CTkFrame(card, fg_color="transparent")
        form.pack(fill="x", padx=20, pady=20)
        
        left_col = ctk.CTkFrame(form, fg_color="transparent")
        left_col.pack(side="left", fill="both", expand=True, padx=(0, 24))
        right_col = ctk.CTkFrame(form, fg_color="transparent")
        right_col.pack(side="right", fill="both", expand=True)
        
        ctk.CTkLabel(left_col, text="Période:", font=ctk.CTkFont(size=14),
            text_color=("#374151", "#D1D5DB")).pack(anchor="w", pady=(0, 8))
        
        period_options = ["Aujourd'hui", "Cette semaine", "Ce mois", "Ce trimestre", "Année en cours"]
        self.period_vars = {}
        period_check = ctk.CTkFrame(left_col, fg_color="transparent")
        period_check.pack(fill="x", pady=(0, 12))
        for i, period in enumerate(period_options):
            var = ctk.CTkBooleanVar(value=True if i == 1 else False)
            self.period_vars[period] = var
            ctk.CTkCheckBox(period_check, text=period, variable=var, font=ctk.CTkFont(size=13),
                text_color=("#374151", "#D1D5DB"), cursor="hand2").pack(anchor="w", pady=2)
        
        ctk.CTkLabel(right_col, text="Type de rapport:", font=ctk.CTkFont(size=14),
            text_color=("#374151", "#D1D5DB")).pack(anchor="w", pady=(0, 8))
        
        type_options = ["Statistiques globales", "Revenus par zone", "Incidents", "Conformité"]
        self.type_vars = {}
        type_check = ctk.CTkFrame(right_col, fg_color="transparent")
        type_check.pack(fill="x", pady=(0, 12))
        for t in type_options:
            var = ctk.CTkBooleanVar(value=True if t == "Statistiques globales" else False)
            self.type_vars[t] = var
            ctk.CTkCheckBox(type_check, text=t, variable=var, font=ctk.CTkFont(size=13),
                text_color=("#374151", "#D1D5DB"), cursor="hand2").pack(anchor="w", pady=2)
        
        ctk.CTkLabel(right_col, text="Destination:", font=ctk.CTkFont(size=14),
            text_color=("#374151", "#D1D5DB")).pack(anchor="w", pady=(0, 8))
        
        dest_options = ["Ministère", "Direction régionale", "Préfecture", "Archivage"]
        self.dest_vars = {}
        dest_check = ctk.CTkFrame(right_col, fg_color="transparent")
        dest_check.pack(fill="x", pady=(0, 12))
        for d in dest_options:
            var = ctk.CTkBooleanVar(value=True if d == "Ministère" else False)
            self.dest_vars[d] = var
            ctk.CTkCheckBox(dest_check, text=d, variable=var, font=ctk.CTkFont(size=13),
                text_color=("#374151", "#D1D5DB"), cursor="hand2").pack(anchor="w", pady=2)
        
        FluentButton(form, text="📊 Générer le rapport", variant="primary", height=44).pack(fill="x", pady=(16, 0))
        
        reports_card = FluentCard(self, title="Rapports récents")
        reports_card.pack(fill="both", expand=True, pady=(0, 16))
        
        reports_data = [
            ("2026-04-25", "Statistiques globales", "Ministère", "Terminé", 1247),
            ("2026-04-24", "Revenus par zone", "Direction régionale", "Terminé", 892),
            ("2026-04-23", "Incidents", "Ministère", "Terminé", 156),
            ("2026-04-22", "Conformité", "Préfecture", "En cours", 43),
            ("2026-04-21", "Statistiques globales", "Archivage", "Terminé", 1247),
            ("2026-04-20", "Revenus par zone", "Ministère", "En attente", 0),
        ]
        
        header_row = ctk.CTkFrame(reports_card, fg_color=("#E5E7EB", "#374151"))
        header_row.pack(fill="x", padx=20, pady=(20, 0))
        for text, w in [("Date", 100), ("Type", 180), ("Destination", 120), ("Statut", 80), ("Enregistrements", 100)]:
            ctk.CTkLabel(header_row, text=text, font=ctk.CTkFont(size=13, weight="bold"),
                text_color=("#374151", "#D1D5DB"), width=w).pack(side="left", padx=12)
        
        self.reports_container = ctk.CTkFrame(reports_card, fg_color="transparent")
        self.reports_container.pack(fill="both", expand=True, padx=20, pady=8)
        
        for report in reports_data:
            ClickableReportRow(self.reports_container, report_data=report)
        
        FluentButton(reports_card, text="Voir plus", variant="secondary", height=36).pack(pady=(0, 16))