# ============================================================
# Module Enregistrements — Gestion des vidéos caméra
# Fichier : desktop_admin/windows/modules/recordings_module.py
# Description : Consultation et gestion des enregistrements caméra
# ============================================================

import customtkinter as ctk
from desktop_admin.theme.components import FluentCard, FluentButton


class RecordingsModule(ctk.CTkFrame):
    """Module de gestion des enregistrements vidéo."""
    
    def __init__(self, master, dashboard=None, user_data=None, **kwargs):
        kwargs.setdefault("fg_color", "transparent")
        super().__init__(master, **kwargs)
        
        self._recordings = self._generate_mock_recordings()
        
        self._build_header()
        self._build_filters()
        self._build_storage_info()
        self._build_table()
    
    def _generate_mock_recordings(self):
        recordings = []
        statuses = ["available", "archived", "deleted"]
        
        for i in range(30):
            recordings.append({
                "id": f"REC{i:06d}",
                "trip_id": f"TR{i:05d}",
                "vehicle": f"T{i:04d}G",
                "driver": f"Driver {i % 15}",
                "created_at": f"2026-05-07 {10+i%12:02d}:{i%60:02d}",
                "duration": f"{5 + i % 25} min",
                "size": f"{100 + i * 15} MB",
                "status": statuses[i % 3],
                "incident": "Oui" if i % 7 == 0 else "Non",
            })
        return recordings
    
    def _build_header(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(0, 16))
        
        ctk.CTkLabel(header, text="📹 Gestion des enregistrements",
                    font=ctk.CTkFont(size=24, weight="bold")).pack(side="left")
        
        FluentButton(header, text="🗑️ Nettoyer anciens", variant="danger").pack(side="right")
    
    def _build_filters(self):
        filters = FluentCard(self, padding=16)
        filters.pack(fill="x", pady=(0, 16))
        
        ctk.CTkEntry(filters, placeholder="Rechercher par trajet ou véhicule...", width=250).pack(side="left", padx=(0, 16))
        ctk.CTkOptionMenu(filters, values=["Tous statuts", "available", "archived", "deleted"],
                         width=150).pack(side="left", padx=(0, 16))
        ctk.CTkOptionMenu(filters, values=["Toutes durées", "< 10 min", "10-30 min", "> 30 min"],
                         width=150).pack(side="left")
        FluentButton(filters, text="Filtrer", variant="secondary").pack(side="right")
    
    def _build_storage_info(self):
        """Informations de stockage."""
        storage = ctk.CTkFrame(self, fg_color="transparent")
        storage.pack(fill="x", pady=(0, 16))
        
        cards = [
            ("💾", "512 GB", "Utilisé", "#1A3A6C"),
            ("📊", "45%", "Capacité", "#009E60"),
            ("🎬", "1,247", "Fichiers", "#7C3AED"),
            ("🗑️", "128", "À supprimer", "#E53E3E"),
        ]
        
        for icon, value, label, color in cards:
            card = FluentCard(storage, padding=16)
            card.pack(side="left", padx=(0, 12), fill="both", expand=True)
            
            ctk.CTkLabel(card, text=icon, font=ctk.CTkFont(size=20)).pack()
            ctk.CTkLabel(card, text=value, font=ctk.CTkFont(size=24, weight="bold"),
                        text_color=color).pack()
            ctk.CTkLabel(card, text=label, font=ctk.CTkFont(size=11),
                        text_color="#6B7280").pack()
    
    def _build_table(self):
        """Tableau des enregistrements."""
        table_card = FluentCard(self, padding=0)
        table_card.pack(fill="both", expand=True)
        
        headers = ["ID", "Trajet", "Véhicule", "Chauffeur", "Date", "Durée", "Taille", "Incident", "Statut", "Actions"]
        
        header_frame = ctk.CTkFrame(table_card, fg_color="#F5F5F5", corner_radius=0)
        header_frame.pack(fill="x")
        
        for h in headers:
            width = 110 if h == "Actions" else 120
            ctk.CTkLabel(header_frame, text=h, font=ctk.CTkFont(size=12, weight="bold"),
                        text_color="#6B7280", width=width).pack(side="left", padx=6, pady=12)
        
        body = ctk.CTkScrollableFrame(table_card, fg_color="transparent")
        body.pack(fill="both", expand=True)
        
        for rec in self._recordings:
            row = ctk.CTkFrame(body, fg_color="transparent")
            row.pack(fill="x")
            
            status_colors = {"available": "#009E60", "archived": "#FCD116", "deleted": "#6B7280"}
            incident_color = "#E53E3E" if rec["incident"] == "Oui" else "#6B7280"
            
            ctk.CTkLabel(row, text=rec["id"], font=ctk.CTkFont(size=10, weight="bold"), width=120).pack(side="left", padx=6, pady=8)
            ctk.CTkLabel(row, text=rec["trip_id"], width=120).pack(side="left", padx=6)
            ctk.CTkLabel(row, text=rec["vehicle"], width=120).pack(side="left", padx=6)
            ctk.CTkLabel(row, text=rec["driver"], width=120, text_color="#6B7280").pack(side="left", padx=6)
            ctk.CTkLabel(row, text=rec["created_at"], width=120, font=ctk.CTkFont(size=10)).pack(side="left", padx=6)
            ctk.CTkLabel(row, text=rec["duration"], width=120).pack(side="left", padx=6)
            ctk.CTkLabel(row, text=rec["size"], width=120).pack(side="left", padx=6)
            ctk.CTkLabel(row, text=rec["incident"], text_color=incident_color, width=100).pack(side="left", padx=6)
            ctk.CTkLabel(row, text=rec["status"].upper(), fg_color=status_colors.get(rec["status"]),
                        text_color="white", corner_radius=4, font=ctk.CTkFont(size=10, weight="bold"),
                        padx=8, pady=2).pack(side="left", padx=6)
            
            actions = ctk.CTkFrame(row, fg_color="transparent", width=110)
            actions.pack(side="left", padx=4)
            
            FluentButton(actions, text="▶", width=28, height=24, fg_color="#1A3A6C").pack(side="left", padx=2)
            FluentButton(actions, text="⬇", width=28, height=24, fg_color="transparent").pack(side="left", padx=2)
            if rec["status"] == "available":
                FluentButton(actions, text="🗑️", width=28, height=24, fg_color="transparent").pack(side="left", padx=2)