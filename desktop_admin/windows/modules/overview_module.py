# ============================================================
# Module Vue d'ensemble — Dashboard Admin MobiTranz
# Fichier : desktop_admin/windows/modules/overview_module.py
# Description : KPIs, graphiques et statistiques via API
# ============================================================

import customtkinter as ctk
from datetime import datetime, timedelta
import threading
from desktop_admin.theme.components import KPICard, FluentCard, FluentButton


class OverviewModule(ctk.CTkFrame):
    """Module Vue d'ensemble avec KPIs et graphiques.
    
    Affiche les métriques clés du système via API backend.
    """
    
    def __init__(self, master, dashboard=None, user_data=None, **kwargs):
        kwargs.setdefault("fg_color", "transparent")
        super().__init__(master, **kwargs)
        
        self._dashboard = dashboard
        self._user_data = user_data or {}
        self._api_client = dashboard.api_client if dashboard else None
        
        self._kpi_data = {}
        
        self._build_header()
        self._build_kpis()
        self._build_charts()
        self._build_recent_activity()
        self._build_system_status()
        
        self._start_auto_refresh()
        self._load_data()
    
    def _load_data(self):
        """Charge les données depuis l'API."""
        if not self._api_client:
            self._show_demo_data()
            return
        
        try:
            kpis = self._api_client.get_kpis()
            self._update_kpis(kpis)
        except Exception as e:
            print(f"Erreur chargement KPIs: {e}")
            self._show_demo_data()
    
    def _show_demo_data(self):
        """Affiche les données de démonstration si API non disponible."""
        demo_kpis = {
            "trips_today": 127,
            "revenue_today": 1250000,
            "active_drivers": 45,
            "active_vehicles": 52,
            "incidents_open": 3,
            "users_total": 1250,
            "trips_trend": 12,
            "revenue_trend": 8,
        }
        self._update_kpis(demo_kpis)
    
    def _update_kpis(self, data):
        """Met à jour les cartes KPIs."""
        self._kpi_data = data
        
        trips = data.get("trips_today", 0)
        self._trips_kpi.set_value(str(trips))
        
        revenue = data.get("revenue_today", 0)
        self._revenue_kpi.set_value(f"{revenue // 1000}k XAF")
        
        drivers = data.get("active_drivers", 0)
        self._drivers_kpi.set_value(str(drivers))
        
        vehicles = data.get("active_vehicles", 0)
        self._vehicles_kpi.set_value(str(vehicles))
        
        incidents = data.get("incidents_open", 0)
        self._incidents_kpi.set_value(str(incidents))
        
        users = data.get("users_total", 0)
        self._users_kpi.set_value(str(users))
        
        if "trips_trend" in data:
            self._trips_kpi.set_trend(data["trips_trend"])
        if "revenue_trend" in data:
            self._revenue_kpi.set_trend(data["revenue_trend"])
    
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
            value="0",
            unit="trajets",
            trend=0,
            icon="🗺️",
            width=200
        )
        self._trips_kpi.pack(side="left", padx=(0, 16))
        
        self._revenue_kpi = KPICard(
            kpi_frame,
            title="Revenus aujourd'hui",
            value="0 XAF",
            unit="XAF",
            trend=0,
            icon="💰",
            width=200
        )
        self._revenue_kpi.pack(side="left", padx=(0, 16))
        
        self._drivers_kpi = KPICard(
            kpi_frame,
            title="Chauffeurs actifs",
            value="0",
            unit="en ligne",
            trend=0,
            icon="🚗",
            width=200
        )
        self._drivers_kpi.pack(side="left", padx=(0, 16))
        
        self._vehicles_kpi = KPICard(
            kpi_frame,
            title="Véhicules actifs",
            value="0",
            unit="véhicules",
            trend=0,
            icon="🚕",
            width=200
        )
        self._vehicles_kpi.pack(side="left", padx=(0, 16))
        
        self._incidents_kpi = KPICard(
            kpi_frame,
            title="Incidents ouverts",
            value="0",
            unit="non résolus",
            trend=0,
            icon="🚨",
            width=200
        )
        self._incidents_kpi.pack(side="left", padx=(0, 16))
        
        self._users_kpi = KPICard(
            kpi_frame,
            title="Total utilisateurs",
            value="0",
            unit="inscrits",
            trend=0,
            icon="👥",
            width=200
        )
        self._users_kpi.pack(side="left")
    
    def _build_charts(self):
        """Graphiques de revenus et trajets."""
        charts_frame = ctk.CTkFrame(self, fg_color="transparent")
        charts_frame.pack(fill="both", expand=True, pady=(0, 24))
        
        revenue_card = FluentCard(charts_frame)
        revenue_card.pack(side="left", fill="both", expand=True, padx=(0, 12))
        
        ctk.CTkLabel(
            revenue_card,
            text="Revenus (30 derniers jours)",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=("#1A1A1A", "white"),
        ).pack(anchor="w", pady=(0, 15))
        
        self._revenue_chart_label = ctk.CTkLabel(
            revenue_card,
            text="📊 Graphique des revenus",
            font=ctk.CTkFont(size=14),
            text_color=("#6B7280", "#9CA3AF"),
        )
        self._revenue_chart_label.pack(expand=True)
        
        trips_card = FluentCard(charts_frame)
        trips_card.pack(side="left", fill="both", expand=True, padx=(12, 0))
        
        ctk.CTkLabel(
            trips_card,
            text="Trajets (30 derniers jours)",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=("#1A1A1A", "white"),
        ).pack(anchor="w", pady=(0, 15))
        
        self._trips_chart_label = ctk.CTkLabel(
            trips_card,
            text="📈 Graphique des trajets",
            font=ctk.CTkFont(size=14),
            text_color=("#6B7280", "#9CA3AF"),
        )
        self._trips_chart_label.pack(expand=True)
    
    def _build_recent_activity(self):
        """Activité récente."""
        activity_card = FluentCard(self)
        activity_card.pack(fill="both", expand=True, pady=(0, 24))
        
        ctk.CTkLabel(
            activity_card,
            text="Activité récente",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=("#1A1A1A", "white"),
        ).pack(anchor="w", pady=(0, 15))
        
        self._activity_list = ctk.CTkScrollableFrame(
            activity_card,
            fg_color="transparent"
        )
        self._activity_list.pack(fill="both", expand=True)
        
        self._add_activity_item("🔄", "Système", "Connexion établie")
        self._add_activity_item("✅", "Admin", "Dashboard chargé")
    
    def _add_activity_item(self, icon: str, source: str, message: str):
        """Ajoute un élément d'activité."""
        item = ctk.CTkFrame(self._activity_list, fg_color=("#F3F4F6", "#1F2937"))
        item.pack(fill="x", pady=(0, 8))
        
        ctk.CTkLabel(
            item,
            text=icon,
            font=ctk.CTkFont(size=16),
            width=30
        ).pack(side="left", padx=(10, 5))
        
        ctk.CTkLabel(
            item,
            text=source,
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=("#1A1A1A", "white"),
        ).pack(side="left", padx=(5, 10))
        
        ctk.CTkLabel(
            item,
            text=message,
            font=ctk.CTkFont(size=13),
            text_color=("#6B7280", "#9CA3AF"),
        ).pack(side="left", padx=(5, 10))
        
        ctk.CTkLabel(
            item,
            text=datetime.now().strftime("%H:%M"),
            font=ctk.CTkFont(size=12),
            text_color=("#9CA3AF", "#6B7280"),
        ).pack(side="right", padx=10)
    
    def _build_system_status(self):
        """Statut du système."""
        status_frame = ctk.CTkFrame(self, fg_color="transparent")
        status_frame.pack(fill="x")
        
        status_card = FluentCard(status_frame)
        status_card.pack(side="left", fill="x", expand=True, padx=(0, 12))
        
        ctk.CTkLabel(
            status_card,
            text="Statut système",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=("#1A1A1A", "white"),
        ).pack(anchor="w", pady=(0, 10))
        
        self._status_labels = {}
        for service in ["API", "Base de données", "Cache Redis", "WebSocket"]:
            row = ctk.CTkFrame(status_card, fg_color="transparent")
            row.pack(fill="x", pady=2)
            
            ctk.CTkLabel(
                row,
                text=service,
                font=ctk.CTkFont(size=13),
                text_color=("#6B7280", "#9CA3AF"),
            ).pack(side="left")
            
            status = ctk.CTkLabel(
                row,
                text="●",
                font=ctk.CTkFont(size=14),
                text_color="#22C55E"
            )
            status.pack(side="right")
            self._status_labels[service] = status
    
    def _refresh_data(self):
        """Rafraîchit les données."""
        self._load_data()
    
    def _start_auto_refresh(self):
        """Démarre le rafraîchissement automatique."""
        self._auto_refresh_running = True

        def refresh_loop():
            import time
            while self._auto_refresh_running:
                time.sleep(60)
                if self._auto_refresh_running:
                    self.after(0, self._load_data)

        thread = threading.Thread(target=refresh_loop, daemon=True)
        thread.start()

    def stop_auto_refresh(self):
        """Arrête le rafraîchissement automatique."""
        self._auto_refresh_running = False
    
    def on_show(self):
        """Callback affiché."""
        self._load_data()