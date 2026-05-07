# ============================================================
# Module Recordings — Administration
# Fichier : desktop_admin/windows/modules/recordings_module.py
# ============================================================

import customtkinter as ctk
from datetime import datetime, timedelta
from desktop_admin.theme.components import FluentCard, KPICard, FluentButton


class RecordingsModule(ctk.CTkFrame):
    """Module de gestion des vidéos."""
    
    _current_filter = "all"
    _date_from = None
    _date_to = None
    _trip_filter = "all"
    
    def __init__(self, master, user_data=None, dashboard=None, **kwargs):
        kwargs.setdefault("fg_color", "transparent")
        kwargs.pop("dashboard", None)
        kwargs.pop("user_data", None)
        super().__init__(master, **kwargs)
        
        self._dashboard = dashboard
        self._user_data = user_data
        self._detail_popup = None
        
        self._recording_data = [
            {"id": "rec_001", "trip": "trip_123", "vehicle": "AA-001-AI", "duration": "12:34", 
             "status": "CHIFFRÉ", "views_24h": 5, "date": "25/04/2026", "thumbnail": "📹", "url": ""},
            {"id": "rec_002", "trip": "trip_124", "vehicle": "AA-002-BK", "duration": "08:21", 
             "status": "CHIFFRÉ", "views_24h": 3, "date": "25/04/2026", "thumbnail": "📹", "url": ""},
            {"id": "rec_003", "trip": "trip_125", "vehicle": "AA-003-CT", "duration": "15:45", 
             "status": "CHIFFRÉ", "views_24h": 8, "date": "24/04/2026", "thumbnail": "📹", "url": ""},
            {"id": "rec_004", "trip": "trip_126", "vehicle": "AA-004-DL", "duration": "10:12", 
             "status": "VU", "views_24h": 12, "date": "24/04/2026", "thumbnail": "📹", "url": ""},
            {"id": "rec_005", "trip": "trip_127", "vehicle": "AA-005-EM", "duration": "06:30", 
             "status": "CHIFFRÉ", "views_24h": 2, "date": "23/04/2026", "thumbnail": "📹", "url": ""},
        ]
        
        self._build_header()
        self._build_kpis()
        self._build_filters()
        self._build_content()
    
    def _build_header(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(0, 16))
        ctk.CTkLabel(header, text="Enregistrements vidéo",
            font=ctk.CTkFont(size=22, weight="bold"), text_color=("#1A1A1A", "white")).pack(side="left")
    
    def _build_kpis(self):
        self._kpi_cards = []
        kpi_frame = ctk.CTkFrame(self, fg_color="transparent")
        kpi_frame.pack(fill="x", pady=(0, 16))
        for i in range(3):
            kpi_frame.grid_columnconfigure(i, weight=1, uniform="kpi")
        
        kpis = [
            ("📹", "Enregistrements", "1,247", "all"),
            ("🔒", "Chiffrés", "1,198", "encrypted"),
            ("👁️", "Vus (24h)", "12", "viewed"),
        ]
        
        for i, (icon, title, value, filter_key) in enumerate(kpis):
            kpi = KPICard(kpi_frame, icon=icon, title=title, value=value)
            kpi.grid(row=0, column=i, sticky="ew", padx=(0, 12 if i < 2 else 0))
            kpi.bind("<Button-1>", lambda e, k=filter_key, t=title: self._on_kpi_click(k, t))
            kpi.configure(cursor="hand2")
            for child in kpi.winfo_children():
                child.configure(cursor="hand2")
            self._kpi_cards.append((kpi, filter_key))
        
        voir_plus_btn = FluentButton(kpi_frame, text="Voir plus →", variant="ghost", icon="📹")
        voir_plus_btn.grid(row=1, column=0, columnspan=3, sticky="e", pady=(12, 0))
        voir_plus_btn.configure(cursor="hand2")
        voir_plus_btn.bind("<Button-1>", lambda e: self._on_voir_plus())
    
    def _build_filters(self):
        filter_frame = ctk.CTkFrame(self, fg_color="transparent")
        filter_frame.pack(fill="x", pady=(0, 16))
        
        self._date_from_entry = ctk.CTkEntry(
            filter_frame,
            placeholder_text="Du (JJ/MM/AAAA)",
            width=140,
        )
        self._date_from_entry.pack(side="left", padx=(0, 8))
        self._date_from_entry.insert(0, (datetime.now() - timedelta(days=30)).strftime("%d/%m/%Y"))
        
        self._date_to_entry = ctk.CTkEntry(
            filter_frame,
            placeholder_text="Au (JJ/MM/AAAA)",
            width=140,
        )
        self._date_to_entry.pack(side="left", padx=(0, 8))
        self._date_to_entry.insert(0, datetime.now().strftime("%d/%m/%Y"))
        
        self._trip_entry = ctk.CTkEntry(
            filter_frame,
            placeholder_text="Filtrer par trajet...",
            width=160,
        )
        self._trip_entry.pack(side="left", padx=(0, 8))
        
        apply_btn = FluentButton(
            filter_frame,
            text="Filtrer",
            variant="secondary",
            icon="🔍",
        )
        apply_btn.pack(side="left", padx=(0, 8))
        apply_btn.bind("<Button-1>", lambda e: self._apply_filters())
        apply_btn.configure(cursor="hand2")
    
    def _build_content(self):
        self._card = FluentCard(self, title="Derniers enregistrements")
        self._card.pack(fill="both", expand=True)
        content = ctk.CTkFrame(self._card, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        headers = [("ID", "id"), ("Trajet", "trip"), ("Véhicule", "vehicle"), ("Durée", "duration"), ("Statut", "status"), ("Vues", "views")]
        header_frame = ctk.CTkFrame(content, fg_color=("#F3F4F6", "#2D3748"))
        header_frame.pack(fill="x", pady=(0, 8))
        
        for h, col_key in headers:
            ctk.CTkLabel(header_frame, text=h, font=ctk.CTkFont(size=12, weight="bold"),
                text_color=("#6B7280", "#9CA3AF"), anchor="center").pack(side="left", padx=16, pady=8)
        
        self._list_frame = ctk.CTkFrame(content, fg_color="transparent")
        self._list_frame.pack(fill="both", expand=True)
        
        self._refresh_list()
    
    def _on_kpi_click(self, filter_key, title):
        self._current_filter = filter_key
        self._refresh_list()
        if self._dashboard:
            self._dashboard._topbar_title.configure(text=f"Enregistrements - {title}")
    
    def _on_voir_plus(self):
        if self._dashboard:
            self._dashboard._on_nav_click("recordings", "recordings")
    
    def _apply_filters(self):
        date_from = self._date_from_entry.get().strip()
        date_to = self._date_to_entry.get().strip()
        trip_filter = self._trip_entry.get().strip()
        
        self._date_from = date_from if date_from else None
        self._date_to = date_to if date_to else None
        self._trip_filter = trip_filter if trip_filter else "all"
        
        self._refresh_list()
    
    def _filter_recordings(self):
        filtered = self._recording_data
        
        if self._current_filter == "encrypted":
            filtered = [r for r in filtered if r["status"] == "CHIFFRÉ"]
        elif self._current_filter == "viewed":
            filtered = [r for r in filtered if r["views_24h"] > 0]
        
        if self._date_from:
            try:
                from_date = datetime.strptime(self._date_from, "%d/%m/%Y")
                filtered = [r for r in filtered if datetime.strptime(r["date"], "%d/%m/%Y") >= from_date]
            except ValueError:
                pass
        
        if self._date_to:
            try:
                to_date = datetime.strptime(self._date_to, "%d/%m/%Y")
                filtered = [r for r in filtered if datetime.strptime(r["date"], "%d/%m/%Y") <= to_date]
            except ValueError:
                pass
        
        if self._trip_filter != "all":
            filtered = [r for r in filtered if self._trip_filter.lower() in r["trip"].lower() or self._trip_filter.lower() in r["vehicle"].lower()]
        
        return filtered
    
    def _refresh_list(self):
        for widget in self._list_frame.winfo_children():
            widget.destroy()
        
        filtered = self._filter_recordings()
        
        for r in filtered:
            row = ctk.CTkFrame(self._list_frame, fg_color=("white", "#2C2C2C"), corner_radius=8)
            row.pack(fill="x", pady=2)
            row.bind("<Button-1>", lambda e, rec=r: self._show_video_player(rec))
            row.bind("<Enter>", lambda e, w=row: self._on_row_hover_enter(e, w))
            row.bind("<Leave>", lambda e, w=row: self._on_row_hover_leave(e, w))
            
            cells = [
                (r["id"], "id"),
                (r["trip"], "trip"),
                (r["vehicle"], "vehicle"),
                (r["duration"], "duration"),
                (r["status"], "status"),
                (str(r["views_24h"]), "views"),
            ]
            
            for cell, col_key in cells:
                ctk.CTkLabel(row, text=cell, font=ctk.CTkFont(size=12),
                    text_color=("#374151", "#D1D5DB"), anchor="center").pack(side="left", padx=16, pady=10)
    
    def _on_row_hover_enter(self, event, widget):
        widget.configure(cursor="hand2", fg_color=("#E5E7EB", "#3D3D3D"))
    
    def _on_row_hover_leave(self, event, widget):
        widget.configure(cursor="", fg_color=("white", "#2C2C2C"))
    
    def _show_video_player(self, recording):
        if self._detail_popup and self._detail_popup.winfo_exists():
            self._detail_popup.destroy()
        
        self._detail_popup = ctk.CTkToplevel(self)
        self._detail_popup.title(f"Enregistrement {recording['id']}")
        self._detail_popup.geometry("800x600")
        self._detail_popup.resizable(True, True)
        
        popup_frame = ctk.CTkFrame(self._detail_popup, fg_color=("#F9FAFB", "#1F2937"))
        popup_frame.pack(fill="both", expand=True, padx=16, pady=16)
        
        title_label = ctk.CTkLabel(
            popup_frame,
            text=f"Enregistrement {recording['id']}",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=("#1A1A1A", "white"),
        )
        title_label.pack(pady=(0, 8))
        
        video_container = ctk.CTkFrame(
            popup_frame,
            fg_color=("#1A1A1A", "#0D0D0D"),
            corner_radius=8,
            height=350,
        )
        video_container.pack(fill="x", pady=(0, 16))
        video_container.pack_propagate(False)
        
        placeholder = ctk.CTkLabel(
            video_container,
            text="🎬\nPrélecture vidéo",
            font=ctk.CTkFont(size=24),
            text_color=("#666666", "#888888"),
        )
        placeholder.place(relx=0.5, rely=0.5, anchor="center")
        
        controls_frame = ctk.CTkFrame(popup_frame, fg_color="transparent")
        controls_frame.pack(fill="x", pady=(0, 16))
        
        ctk.CTkLabel(
            controls_frame,
            text="Contrôles",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=("#1A1A1A", "white"),
        ).pack(side="left")
        
        controls_frame_right = ctk.CTkFrame(controls_frame, fg_color="transparent")
        controls_frame_right.pack(side="right")
        
        play_btn = ctk.CTkButton(
            controls_frame_right,
            text="▶ Lecture",
            fg_color="#1A3A6C",
            hover_color="#2A4A7C",
            width=100,
            command=lambda: self._play_video(recording),
        )
        play_btn.pack(side="left", padx=(0, 8))
        
        pause_btn = ctk.CTkButton(
            controls_frame_right,
            text="⏸ Pause",
            fg_color="#6B7280",
            hover_color="#4B7280",
            width=100,
            command=lambda: self._pause_video(),
        )
        pause_btn.pack(side="left", padx=(0, 8))
        
        download_btn = ctk.CTkButton(
            controls_frame_right,
            text="⬇ Télécharger",
            fg_color="#009E60",
            hover_color="#00AE70",
            width=120,
            command=lambda: self._download_video(recording),
        )
        download_btn.pack(side="left")
        
        details_frame = ctk.CTkFrame(popup_frame, fg_color="transparent")
        details_frame.pack(fill="x")
        
        details = [
            ("Trajet", recording["trip"]),
            ("Véhicule", recording["vehicle"]),
            ("Durée", recording["duration"]),
            ("Statut", recording["status"]),
            ("Vues (24h)", str(recording["views_24h"])),
            ("Date", recording["date"]),
        ]
        
        for label, value in details:
            row = ctk.CTkFrame(details_frame, fg_color="transparent")
            row.pack(fill="x", pady=4)
            ctk.CTkLabel(
                row,
                text=f"{label}:",
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=("#6B7280", "#9CA3AF"),
            ).pack(side="left")
            ctk.CTkLabel(
                row,
                text=value,
                font=ctk.CTkFont(size=12),
                text_color=("#1A1A1A", "white"),
            ).pack(side="left", padx=(8, 0))
        
        close_btn = ctk.CTkButton(
            popup_frame,
            text="Fermer",
            fg_color="#6B7280",
            hover_color="#4B7280",
            width=120,
            command=self._detail_popup.destroy,
        )
        close_btn.pack(pady=(16, 0))
    
    def _play_video(self, recording):
        pass
    
    def _pause_video(self):
        pass
    
    def _download_video(self, recording):
        pass