# ============================================================
# Module Incidents — Administration
# Fichier : desktop_admin/windows/modules/incidents_module.py
# ============================================================

import customtkinter as ctk
from desktop_admin.theme.components import FluentCard, KPICard, FluentButton
from datetime import datetime


class IncidentsModule(ctk.CTkFrame):
    """Module de gestion des incidents."""
    
    def __init__(self, master, user_data=None, dashboard=None, **kwargs):
        kwargs.setdefault("fg_color", "transparent")
        kwargs.pop("dashboard", None)
        kwargs.pop("user_data", None)
        super().__init__(master, **kwargs)
        
        self.current_filter = {"type": "ALL", "status": "ALL"}
        
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(0, 16))
        ctk.CTkLabel(header, text="Incidents SOS",
            font=ctk.CTkFont(size=22, weight="bold"), text_color=("#E53E3E", "#FC8181")).pack(side="left")
        
        right = ctk.CTkFrame(header, fg_color="transparent")
        right.pack(side="right")
        ctk.CTkLabel(right, text=f"🕐 {datetime.now().strftime('%H:%M:%S')}",
            font=ctk.CTkFont(size=12), text_color=("#9A9A9A", "#6D6D6D")).pack(side="right")
        
        filters_frame = ctk.CTkFrame(self, fg_color="transparent")
        filters_frame.pack(fill="x", pady=(0, 16))
        
        ctk.CTkLabel(filters_frame, text="Filtrer par:", font=ctk.CTkFont(size=12, weight="bold")).pack(side="left", padx=(0, 8))
        
        self.type_var = ctk.StringVar(value="ALL")
        type_menu = ctk.CTkOptionMenu(filters_frame, variable=self.type_var, values=["ALL", "SOS", "DISPUTE", "ACCIDENT", "TECHNIQUE"],
            command=lambda x: self.apply_filters())
        type_menu.pack(side="left", padx=8)
        
        self.status_var = ctk.StringVar(value="ALL")
        status_menu = ctk.CTkOptionMenu(filters_frame, variable=self.status_var, values=["ALL", "OUVERT", "EN COURS", "RÉSOLU"],
            command=lambda x: self.apply_filters())
        status_menu.pack(side="left", padx=8)
        
        kpi_frame = ctk.CTkFrame(self, fg_color="transparent")
        kpi_frame.pack(fill="x")
        for i in range(4):
            kpi_frame.grid_columnconfigure(i, weight=1, uniform="kpi")
        
        self.kpi_data = [("🚨", "Total", "23", "ALL"), ("⏳", "Ouverts", "3", "OUVERT"), ("🔄", "En cours", "5", "EN COURS"), ("✅", "Résolus", "15", "RÉSOLU")]
        self.kpi_cards = []
        for i, (icon, title, value, filter_key) in enumerate(self.kpi_data):
            card = self._create_clickable_kpi(kpi_frame, icon, title, value, filter_key, i)
            card.grid(row=0, column=i, sticky="ew", padx=(0, 12 if i < 3 else 0))
            self.kpi_cards.append(card)
        
        see_more_btn = FluentButton(kpi_frame, text="Voir plus", width=120)
        see_more_btn.grid(row=0, column=4, padx=(12, 0))
        see_more_btn.configure(command=lambda: self.see_more())
        
        card = FluentCard(self, title="Incidents récents")
        card.pack(fill="both", expand=True, pady=(16, 0))
        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        self.headers = ["ID", "Type", "Trajet", "Statut", "Signalé à"]
        header_frame = ctk.CTkFrame(content, fg_color=("#FEE2E2", "#4A1A1A"))
        header_frame.pack(fill="x", pady=(0, 8))
        for h in self.headers:
            ctk.CTkLabel(header_frame, text=h, font=ctk.CTkFont(size=12, weight="bold"),
                text_color=("#991B1B", "#FCA5A5")).pack(side="left", padx=16, pady=8)
        
        self.all_incidents = [
            {"id": "inc_001", "type": "🚨 SOS", "trip": "trip_123", "status": "OUVERT", "time": "14:32", "location": "Avenue des Champs-Élysées, Paris", "participants": "Driver: Jean M. | Passenger: Marie L.", "timeline": "14:32 - Signalement reçu\n14:35 - Notification envoyée\n14:40 - Dispatcher en contact", "resolution": "En attente de confirmation"},
            {"id": "inc_002", "type": "⚠️ DISPUTE", "trip": "trip_124", "status": "EN COURS", "time": "13:45", "location": "Rue de la République, Lyon", "participants": "Driver: Pierre D. | Passenger: Sophie R.", "timeline": "13:45 - Signalement reçu\n13:47 - Appel initiés\n13:50 - Médiation en cours", "resolution": "Médiation en cours - réponse attendue"},
            {"id": "inc_003", "type": "🚗 ACCIDENT", "trip": "trip_125", "status": "RÉSOLU", "time": "hier", "location": "Boulevard Saint-Germain, Paris", "participants": "Driver: Marc T. | Passenger: Anne B.", "timeline": "Hier 10:30 - Signalement reçu\n10:32 - Services d'urgence prévenus\n11:15 - Incident clos", "resolution": "Résolu - Constat à l'amiable établi"},
            {"id": "inc_004", "type": "🚨 SOS", "trip": "trip_126", "status": "OUVERT", "time": "12:15", "location": "Place Vendôme, Paris", "participants": "Driver: Luc F. | Passenger: Emma K.", "timeline": "12:15 - Signalement reçu\n12:18 - Notification envoyée", "resolution": "En attente"},
            {"id": "inc_005", "type": "⚡ TECHNIQUE", "trip": "trip_127", "status": "EN COURS", "time": "11:00", "location": " Avenue de la Grande Armée, Paris", "participants": "Driver: Nicolas S. | Passenger: Clara M.", "timeline": "11:00 - Signalement reçu\n11:05 - Support technique alerté", "resolution": "Diagnostic en cours"},
        ]
        
        self.incident_rows = []
        self.content = content
        self.populate_incidents()
    
    def _create_clickable_kpi(self, parent, icon, title, value, filter_key, index):
        card = ctk.CTkFrame(parent, fg_color=("#FFFFFF", "#2C2C2C"), corner_radius=12, border_width=1, border_color=("#E5E7EB", "#3F3F3F"))
        card.filter_key = filter_key
        card.bind("<Button-1>", lambda e, k=filter_key: self.filter_by_kpi(k))
        for child in card.winfo_children():
            child.bind("<Button-1>", lambda e, k=filter_key: self.filter_by_kpi(k))
        icon_label = ctk.CTkLabel(card, text=f"{icon} {title}\n{value}", font=ctk.CTkFont(size=14, weight="bold"),
            text_color=("#E53E3E", "#FC8181"), justify="center")
        icon_label.pack(pady=16, padx=16)
        card._label = icon_label
        
        def on_enter(e):
            card.configure(cursor="hand2")
            card.configure(border_color=("#E53E3E", "#FC8181"))
        def on_leave(e):
            card.configure(cursor="")
            card.configure(border_color=("#E5E7EB", "#3F3F3F"))
        
        card.bind("<Enter>", on_enter)
        card.bind("<Leave>", on_leave)
        icon_label.bind("<Enter>", on_enter)
        icon_label.bind("<Leave>", on_leave)
        
        return card
    
    def filter_by_kpi(self, filter_key):
        if filter_key == "ALL":
            self.status_var.set("ALL")
            self.type_var.set("ALL")
        else:
            self.status_var.set(filter_key)
        self.apply_filters()
    
    def apply_filters(self):
        self.current_filter["type"] = self.type_var.get()
        self.current_filter["status"] = self.status_var.get()
        self.populate_incidents()
    
    def populate_incidents(self):
        for row in self.incident_rows:
            row.destroy()
        self.incident_rows = []
        
        filtered = self.all_incidents
        if self.current_filter["type"] != "ALL":
            type_map = {"SOS": "🚨 SOS", "DISPUTE": "⚠️ DISPUTE", "ACCIDENT": "🚗 ACCIDENT", "TECHNIQUE": "⚡ TECHNIQUE"}
            filtered = [inc for inc in filtered if inc["type"] == type_map.get(self.current_filter["type"], inc["type"])]
        if self.current_filter["status"] != "ALL":
            filtered = [inc for inc in filtered if inc["status"] == self.current_filter["status"]]
        
        for inc in filtered:
            row = ctk.CTkFrame(self.content, fg_color=("white", "#2C2C2C"), corner_radius=8, cursor="hand2")
            row.pack(fill="x", pady=2)
            row.incident_data = inc
            
            def on_enter(e):
                row.configure(fg_color=("#FEE2E2", "#3A1A1A"))
            def on_leave(e):
                row.configure(fg_color=("white", "#2C2C2C"))
            
            row.bind("<Enter>", on_enter)
            row.bind("<Leave>", on_leave)
            
            for child in row.winfo_children():
                child.bind("<Enter>", on_enter)
                child.bind("<Leave>", on_leave)
                child.bind("<Button-1>", lambda e, data=inc: self.show_incident_detail(data))
            
            row.bind("<Button-1>", lambda e, data=inc: self.show_incident_detail(data))
            
            for key in ["id", "type", "trip", "status", "time"]:
                ctk.CTkLabel(row, text=inc[key], font=ctk.CTkFont(size=12), text_color=("#374151", "#D1D5DB")).pack(side="left", padx=16, pady=10)
            
            self.incident_rows.append(row)
    
    def show_incident_detail(self, incident):
        if hasattr(self, 'detail_drawer') and self.detail_drawer is not None:
            self.detail_drawer.destroy()
        
        self.detail_drawer = ctk.CTkToplevel(self)
        self.detail_drawer.title(f"Incident {incident['id']}")
        self.detail_drawer.geometry("500x600")
        self.detail_drawer.configure(fg_color=("white", "#1E1E1E"))
        
        title_frame = ctk.CTkFrame(self.detail_drawer, fg_color=("#FEE2E2", "#4A1A1A"))
        title_frame.pack(fill="x", pady=0)
        ctk.CTkLabel(title_frame, text=f"{incident['type']} - {incident['id']}", font=ctk.CTkFont(size=18, weight="bold"),
            text_color=("#991B1B", "#FCA5A5"), pady=12).pack()
        
        close_btn = ctk.CTkButton(title_frame, text="✕", width=30, height=30, fg_color="transparent",
            text_color=("#991B1B", "#FCA5A5"), hover_color=("#FECACA", "#6B2A2A"), command=self.detail_drawer.destroy)
        close_btn.place(relx=0.95, rely=0.5, anchor="center")
        
        scroll = ctk.CTkScrollableFrame(self.detail_drawer, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=20, pady=20)
        
        sections = [
            ("📍 Localisation", incident["location"]),
            ("👥 Participants", incident["participants"]),
            ("📋 Statut", incident["status"]),
            ("🕐 Horodatage", incident["time"]),
            ("📝 Résolution", incident["resolution"]),
        ]
        
        for title, content_text in sections:
            section = ctk.CTkFrame(scroll, fg_color=("#F3F4F6", "#2C2C2C"), corner_radius=8)
            section.pack(fill="x", pady=8)
            ctk.CTkLabel(section, text=title, font=ctk.CTkFont(size=12, weight="bold"),
                text_color=("#374151", "#D1D5DB"), padx=12, pady=(12, 4)).pack(anchor="w")
            ctk.CTkLabel(section, text=content_text, font=ctk.CTkFont(size=11),
                text_color=("#6B7280", "#9CA3AF"), padx=12, pady=(0, 12), wraplength=420, justify="left").pack(anchor="w")
        
        timeline_section = ctk.CTkFrame(scroll, fg_color=("#F3F4F6", "#2C2C2C"), corner_radius=8)
        timeline_section.pack(fill="x", pady=8)
        ctk.CTkLabel(timeline_section, text="📅 Timeline", font=ctk.CTkFont(size=12, weight="bold"),
            text_color=("#374151", "#D1D5DB"), padx=12, pady=(12, 4)).pack(anchor="w")
        ctk.CTkLabel(timeline_section, text=incident["timeline"], font=ctk.CTkFont(size=11),
            text_color=("#6B7280", "#9CA3AF"), padx=12, pady=(0, 12), justify="left").pack(anchor="w")
    
    def see_more(self):
        self.status_var.set("ALL")
        self.type_var.set("ALL")
        self.apply_filters()