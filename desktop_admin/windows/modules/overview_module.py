# ============================================================
# Module Vue d'ensemble — Dashboard Admin MobiTranz
# Fichier : desktop_admin/windows/modules/overview_module.py
# Description : KPIs, graphiques et statistiques en temps réel
# ============================================================

import customtkinter as ctk
from datetime import datetime, timedelta
import random
import threading
from desktop_admin.theme.components import KPICard, FluentCard, FluentButton


class OverviewModule(ctk.CTkFrame):
    """Module Vue d'ensemble avec KPIs et graphiques.
    
    Affiche les métriques clés du système avec tendances,
    graphiques de activité, et alertes en temps réel.
    """
    
    def __init__(self, master, dashboard=None, user_data=None, **kwargs):
        kwargs.setdefault("fg_color", "transparent")
        super().__init__(master, **kwargs)
        
        self._dashboard = dashboard
        self._user_data = user_data or {}
        
        self._build_header()
        self._build_kpis()
        self._build_charts()
        self._build_recent_activity()
        self._build_system_status()
        
        self._start_auto_refresh()
    
    def _build_header(self):
        """En-tête avec titre et actions."""
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(0, 20))
        
        title_frame = ctk.CTkFrame(header, fg_color="transparent")
        title_frame.pack(side="left")
        
        ctk.CTkLabel(
            title_frame,
            text="Vue d'ensemble",
            font=ctk.CTkFont(family="Segoe UI Variable Display", size=28, weight="bold"),
            text_color=("#1A1A1A", "white"),
        ).pack(anchor="w")
        
        ctk.CTkLabel(
            title_frame,
            text="Bienvenue sur MobiTranz Admin",
            font=ctk.CTkFont(size=13),
            text_color=("#6B7280", "#9CA3AF"),
        ).pack(anchor="w", pady=(4, 0))
        
        actions = ctk.CTkFrame(header, fg_color="transparent")
        actions.pack(side="right")
        
        self._refresh_btn = FluentButton(
            actions,
            text="🔄 Actualiser",
            variant="secondary",
            command=self._refresh_data
        )
        self._refresh_btn.pack(side="right")
    
    def _build_kpis(self):
        """Cartes KPIs principales."""
        kpi_frame = ctk.CTkFrame(self, fg_color="transparent")
        kpi_frame.pack(fill="x", pady=(0, 24))
        
        self._trips_kpi = KPICard(
            kpi_frame,
            title="Trajets aujourd'hui",
            value="127",
            unit="trajets",
            trend=12,
            icon="🗺️",
            accent_color="#1A3A6C"
        )
        self._trips_kpi.pack(side="left", padx=(0, 16))
        
        self._revenue_kpi = KPICard(
            kpi_frame,
            title="Revenus du jour",
            value="1.2M",
            unit="FCFA",
            trend=8,
            icon="💰",
            accent_color="#009E60"
        )
        self._revenue_kpi.pack(side="left", padx=(0, 16))
        
        self._drivers_kpi = KPICard(
            kpi_frame,
            title="Conducteurs actifs",
            value="45",
            unit="en ligne",
            trend=5,
            icon="🚗",
            accent_color="#FCD116"
        )
        self._drivers_kpi.pack(side="left", padx=(0, 16))
        
        self._incidents_kpi = KPICard(
            kpi_frame,
            title="Incidents ouverts",
            value="3",
            unit="alertes",
            trend=-25,
            icon="🚨",
            accent_color="#E53E3E"
        )
        self._incidents_kpi.pack(side="left", padx=(0, 16))
        
        self._clients_kpi = KPICard(
            kpi_frame,
            title="Clients actifs",
            value="2,847",
            unit="utilisateurs",
            trend=15,
            icon="👥",
            accent_color="#7C3AED"
        )
        self._clients_kpi.pack(side="left")
    
    def _build_charts(self):
        """Graphiques de l'activité."""
        charts_frame = ctk.CTkFrame(self, fg_color="transparent")
        charts_frame.pack(fill="both", expand=True, pady=(0, 24))
        charts_frame.grid_columnconfigure(0, weight=1)
        charts_frame.grid_columnconfigure(1, weight=1)
        
        self._build_trips_chart(charts_frame)
        self._build_revenue_chart(charts_frame)
    
    def _build_trips_chart(self, parent):
        """Graphique des trajets par heure."""
        card = FluentCard(parent, title="Trajets par heure", padding=16)
        card.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        
        chart_frame = ctk.CTkFrame(card, fg_color="transparent")
        chart_frame.pack(fill="both", expand=True, pady=(16, 0))
        
        hours = ["6h", "8h", "10h", "12h", "14h", "16h", "18h", "20h", "22h"]
        values = [12, 45, 28, 35, 22, 48, 65, 32, 15]
        
        max_val = max(values) if values else 1
        
        bar_frame = ctk.CTkFrame(chart_frame, fg_color="transparent")
        bar_frame.pack(fill="both", expand=True)
        
        for hour, value in zip(hours, values):
            bar_container = ctk.CTkFrame(bar_frame, fg_color="transparent")
            bar_container.pack(side="left", fill="both", expand=True)
            
            bar_height = (value / max_val) * 150
            
            bar = ctk.CTkFrame(
                bar_container,
                fg_color="#1A3A6C",
                corner_radius=4,
                height=max(bar_height, 4)
            )
            bar.pack(side="bottom", pady=(0, 4))
            
            ctk.CTkLabel(
                bar_container,
                text=str(value),
                font=ctk.CTkFont(size=10, weight="bold"),
                text_color="#1A3A6C"
            ).pack(side="bottom")
            
            ctk.CTkLabel(
                bar_container,
                text=hour,
                font=ctk.CTkFont(size=9),
                text_color="#6B7280"
            ).pack(side="bottom", pady=(4, 0))
    
    def _build_revenue_chart(self, parent):
        """Graphique des revenus par jour."""
        card = FluentCard(parent, title="Revenus (7 derniers jours)", padding=16)
        card.grid(row=0, column=1, sticky="nsew", padx=(12, 0))
        
        chart_frame = ctk.CTkFrame(card, fg_color="transparent")
        chart_frame.pack(fill="both", expand=True, pady=(16, 0))
        
        days = ["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"]
        values = [850000, 920000, 780000, 1100000, 1250000, 980000, 650000]
        
        max_val = max(values) if values else 1
        
        bar_frame = ctk.CTkFrame(chart_frame, fg_color="transparent")
        bar_frame.pack(fill="both", expand=True)
        
        for day, value in zip(days, values):
            bar_container = ctk.CTkFrame(bar_frame, fg_color="transparent")
            bar_container.pack(side="left", fill="both", expand=True)
            
            bar_height = (value / max_val) * 150
            
            bar = ctk.CTkFrame(
                bar_container,
                fg_color="#009E60",
                corner_radius=4,
                height=max(bar_height, 4)
            )
            bar.pack(side="bottom", pady=(0, 4))
            
            amount = f"{value // 1000}k"
            ctk.CTkLabel(
                bar_container,
                text=amount,
                font=ctk.CTkFont(size=10, weight="bold"),
                text_color="#009E60"
            ).pack(side="bottom")
            
            ctk.CTkLabel(
                bar_container,
                text=day,
                font=ctk.CTkFont(size=9),
                text_color="#6B7280"
            ).pack(side="bottom", pady=(4, 0))
    
    def _build_recent_activity(self):
        """Activité récente et alertes."""
        activity_frame = ctk.CTkFrame(self, fg_color="transparent")
        activity_frame.pack(fill="x", pady=(0, 24))
        activity_frame.grid_columnconfigure(0, weight=1)
        activity_frame.grid_columnconfigure(1, weight=1)
        
        self._build_recent_trips(activity_frame)
        self._build_recent_alerts(activity_frame)
    
    def _build_recent_trips(self, parent):
        """Liste des trajets récents."""
        card = FluentCard(parent, title="Trajets récents", padding=16)
        card.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        
        self._trips_list = ctk.CTkScrollableFrame(card, fg_color="transparent")
        self._trips_list.pack(fill="both", expand=True)
        
        for i in range(5):
            self._add_trip_item(
                self._trips_list,
                f"Trip-{1000+i}",
                ["Libreville", "Owendo"][i % 2],
                ["2500", "3500", "4000", "3000", "2800"][i],
                ["En cours", "Terminé", "Terminé", "En cours", "Terminé"][i]
            )
    
    def _add_trip_item(self, parent, trip_id, route, amount, status):
        """Ajoute un élément de trajet à la liste."""
        item = ctk.CTkFrame(parent, fg_color=("#F5F5F5", "#2C2C2C"), corner_radius=8)
        item.pack(fill="x", pady=4)
        
        status_colors = {
            "En cours": ("#1A3A6C", "white"),
            "Terminé": ("#009E60", "white"),
            "Annulé": ("#E53E3E", "white")
        }
        
        bg, fg = status_colors.get(status, ("#6B7280", "white"))
        
        ctk.CTkLabel(
            item,
            text=trip_id,
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=("#1A1A1A", "white"),
            width=80
        ).pack(side="left", padx=12, pady=12)
        
        ctk.CTkLabel(
            item,
            text=f"📍 {route}",
            font=ctk.CTkFont(size=12),
            text_color=("#6B7280", "#9CA3AF"),
        ).pack(side="left", padx=12)
        
        ctk.CTkLabel(
            item,
            text=f"{amount} XAF",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=("#009E60", "#4DC882"),
        ).pack(side="left", padx=12)
        
        status_label = ctk.CTkLabel(
            item,
            text=status,
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=fg,
            fg_color=bg,
            corner_radius=4,
            padx=8, pady=2
        )
        status_label.pack(side="right", padx=12)
    
    def _build_recent_alerts(self, parent):
        """Liste des alertes récentes."""
        card = FluentCard(parent, title="Alertes récentes", padding=16)
        card.grid(row=0, column=1, sticky="nsew", padx=(12, 0))
        
        alerts_list = ctk.CTkScrollableFrame(card, fg_color="transparent")
        alerts_list.pack(fill="both", expand=True)
        
        alerts = [
            ("🚨", "SOS déclenché", "Il y a 5 min", "#E53E3E"),
            ("⚠️", "Déviation de route", "Il y a 12 min", "#FCD116"),
            ("ℹ️", "Nouveau driver validé", "Il y a 28 min", "#1A3A6C"),
            ("✅", "Incident résolu", "Il y a 1h", "#009E60"),
        ]
        
        for icon, title, time, color in alerts:
            item = ctk.CTkFrame(alerts_list, fg_color="transparent")
            item.pack(fill="x", pady=4)
            
            ctk.CTkLabel(
                item,
                text=icon,
                font=ctk.CTkFont(size=18),
            ).pack(side="left", padx=8)
            
            ctk.CTkLabel(
                item,
                text=title,
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=("#1A1A1A", "white"),
            ).pack(side="left", padx=8)
            
            ctk.CTkLabel(
                item,
                text=time,
                font=ctk.CTkFont(size=10),
                text_color="#6B7280",
            ).pack(side="right", padx=8)
    
    def _build_system_status(self):
        """État du système."""
        status_frame = FluentCard(self, title="État du système", padding=16)
        status_frame.pack(fill="x")
        
        grid = ctk.CTkFrame(status_frame, fg_color="transparent")
        grid.pack(fill="x", pady=(16, 0))
        
        items = [
            ("🟢", "Base de données", "Connectée", "#009E60"),
            ("🟢", "API Backend", "En ligne", "#009E60"),
            ("🟢", "Redis Cache", "Actif", "#009E60"),
            ("🟡", "MinIO Stockage", "95% utilisé", "#FCD116"),
            ("🟢", "WebSocket", "Connecté", "#009E60"),
            ("🟢", "Caméra Raspberry", "42 en ligne", "#009E60"),
        ]
        
        for i, (icon, name, status, color) in enumerate(items):
            col = i % 3
            row = i // 3
            
            item = ctk.CTkFrame(grid, fg_color="transparent")
            item.grid(row=row, column=col, sticky="w", padx=16, pady=8)
            
            ctk.CTkLabel(
                item,
                text=icon,
                font=ctk.CTkFont(size=16),
            ).pack(side="left")
            
            ctk.CTkLabel(
                item,
                text=f"  {name}",
                font=ctk.CTkFont(size=12),
                text_color=("#1A1A1A", "white"),
            ).pack(side="left")
            
            ctk.CTkLabel(
                item,
                text=f"  {status}",
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color=color,
            ).pack(side="left")
    
    def _refresh_data(self):
        """Actualise les données du dashboard."""
        self._refresh_btn.set_loading(True)
        
        def refresh():
            import time
            time.sleep(1)
            
            new_values = {
                "trips": str(random.randint(100, 200)),
                "revenue": f"{random.randint(800, 1500)}K",
                "drivers": str(random.randint(30, 60)),
                "incidents": str(random.randint(0, 10)),
            }
            
            self.after(0, lambda: self._update_kpis(new_values))
            self.after(0, lambda: self._refresh_btn.set_loading(False))
        
        threading.Thread(target=refresh, daemon=True).start()
    
    def _update_kpis(self, values):
        """Met à jour les valeurs des KPIs."""
        self._trips_kpi.update_value(values["trips"])
        self._revenue_kpi.update_value(values["revenue"])
        self._drivers_kpi.update_value(values["drivers"])
        self._incidents_kpi.update_value(values["incidents"])
    
    def _start_auto_refresh(self):
        """Démarre l'actualisation automatique."""
        def auto_refresh():
            while True:
                import time
                time.sleep(60)
                self.after(0, self._refresh_data)
        
        threading.Thread(target=auto_refresh, daemon=True).start()