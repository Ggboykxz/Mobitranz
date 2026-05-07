# ============================================================
# Fenêtre principale Dashboard Admin — Layout Fluent Design
# Fichier : desktop_admin/windows/dashboard_window.py
# Description : Sidebar + ContentArea avec modules dynamiques
# ============================================================

import customtkinter as ctk
from desktop_admin.theme.components import FluentSidebar, KPICard, FluentCard
from desktop_admin.api_service import AdminAPIClient


class MainWindow(ctk.CTkFrame):
    """Fenêtre principale de l'administration MobiTranz.
    
    Layout :
    ┌─────────────────────────────────────────────────────────┐
    │  TOPBAR (titre module + profil utilisateur)                │
    ├──────────┬──────────────────────────────────────────────┤
    │ SIDEBAR  │          CONTENT AREA                       │
    │ (240px)  │     (module chargé dynamiquement)       │
    └──────────┴──────────────────────────────────────────────┘
    """
    
    NAV_ITEMS = [
        ("📊", "Vue d'ensemble",   "overview"),
        ("👥", "Utilisateurs",     "users"),
        ("🚗", "Conducteurs",      "drivers"),
        ("🚕", "Véhicules",        "vehicles"),
        ("🗺️",  "Trajets",          "trips"),
        ("💳", "Transactions",     "transactions"),
        ("🚨", "Incidents",        "incidents"),
        ("📹", "Enregistrements",  "recordings"),
        ("📊", "Rapports",         "reports"),
        ("⚙️",  "Paramètres",       "settings"),
        ("🔒", "Sécurité & Logs",  "audit"),
    ]
    
    def __init__(self, master, user_data=None, **kwargs):
        kwargs.setdefault("fg_color", ("#F3F3F3", "#202020"))
        kwargs.setdefault("corner_radius", 0)
        super().__init__(master, **kwargs)
        
        self._user_data = user_data or {}
        self._active_module = None
        
        # API Client - connecté au backend
        self.api_client = AdminAPIClient()
        
        # Layout principal
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        self._build_topbar()
        self._build_sidebar()
        self._build_content_area()
        
        self._load_module("overview")
    
    def _build_topbar(self):
        """Barre supérieure avec titre et profil."""
        topbar = ctk.CTkFrame(
            self,
            height=60,
            corner_radius=0,
            fg_color=("white", "#2C2C2C"),
            border_width=0,
        )
        topbar.grid(row=0, column=0, columnspan=2, sticky="ew")
        topbar.grid_columnconfigure(1, weight=1)
        topbar.grid_propagate(False)
        
        self._topbar_title = ctk.CTkLabel(
            topbar,
            text="Vue d'ensemble",
            font=ctk.CTkFont(family="Segoe UI Variable Display", size=18, weight="bold"),
            text_color=("#1A1A1A", "white"),
            anchor="w"
        )
        self._topbar_title.grid(row=0, column=1, sticky="w", padx=24, pady=16)
        
        # Profil utilisateur
        profile_frame = ctk.CTkFrame(topbar, fg_color="transparent")
        profile_frame.grid(row=0, column=2, sticky="e", padx=16)
        
        email = self._user_data.get("email", "admin@mobitranz.ga")
        initials = email[0].upper() + (email[1].upper() if len(email) > 1 else "")
        
        ctk.CTkLabel(
            profile_frame,
            text=initials,
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="white",
            fg_color="#1A3A6C",
            width=36, height=36,
            corner_radius=18,
        ).pack(side="right", padx=(8, 0))
        
        ctk.CTkLabel(
            profile_frame,
            text=email,
            font=ctk.CTkFont(size=12),
            text_color=("#5C5C5C", "#ABABAB"),
        ).pack(side="right")
        
        # Divider
        ctk.CTkFrame(self, height=1, fg_color=("#E5E5E5", "#3D3D3D"), corner_radius=0).grid(
            row=0, column=0, columnspan=2, sticky="sew"
        )
    
    def _build_sidebar(self):
        """Sidebar de navigation."""
        self._sidebar = FluentSidebar(
            self,
            items=[(icon, label, lambda l=label, m=module: self._on_nav_click(l, m))
                   for icon, label, module in self.NAV_ITEMS],
            logo_text="MobiTranz",
        )
        self._sidebar.grid(row=1, column=0, sticky="nsew")
    
    def _build_content_area(self):
        """Zone de contenu dynamique."""
        self._content_frame = ctk.CTkScrollableFrame(
            self,
            fg_color=("#F3F3F3", "#202020"),
            corner_radius=0,
            scrollbar_button_color=("#CCCCCC", "#555555"),
        )
        self._content_frame.grid(row=1, column=1, sticky="nsew")
        self._content_frame.grid_columnconfigure(0, weight=1)
    
    def _on_nav_click(self, label: str, module: str):
        """Callback navigation."""
        self._topbar_title.configure(text=label)
        self._load_module(module)
    
    def _load_module(self, module_name: str):
        """Charge dynamiquement un module."""
        for widget in self._content_frame.winfo_children():
            widget.destroy()
        
        module_map = {
            "overview": "OverviewModule",
            "users": "UsersModule",
            "drivers": "DriversModule", 
            "vehicles": "VehiclesModule",
            "trips": "TripsModule",
            "transactions": "TransactionsModule",
            "incidents": "IncidentsModule",
            "recordings": "RecordingsModule",
            "reports": "ReportsModule",
            "settings": "SettingsModule",
            "audit": "AuditModule",
        }
        
        class_name = module_map.get(module_name, f"{module_name.capitalize()}Module")
        
        try:
            import importlib
            mod = importlib.import_module(f"desktop_admin.windows.modules.{module_name}_module")
            ModuleClass = getattr(mod, class_name)
            module_widget = ModuleClass(self._content_frame, dashboard=self, user_data=self._user_data)
            module_widget.pack(fill="both", expand=True, padx=24, pady=24)
        except (ImportError, AttributeError):
            self._render_placeholder(module_name)
    
    def _render_placeholder(self, module_name: str):
        """Placeholder pour modules non développés."""
        frame = ctk.CTkFrame(self._content_frame, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=24, pady=80)
        
        ctk.CTkLabel(
            frame,
            text="🚧",
            font=ctk.CTkFont(size=64),
        ).pack()
        ctk.CTkLabel(
            frame,
            text=f"Module '{module_name}' en développement",
            font=ctk.CTkFont(family="Segoe UI Variable Display", size=20, weight="bold"),
            text_color=("#5C5C5C", "#ABABAB"),
        ).pack(pady=8)
    
    def set_module_title(self, title: str):
        """Met à jour le titre du module dans la topbar."""
        if hasattr(self, '_topbar_title'):
            self._topbar_title.configure(text=title)