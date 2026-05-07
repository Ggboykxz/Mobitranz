# ============================================================
# Module Trajets — Suivi des trajets MobiTranz
# Fichier : desktop_admin/windows/modules/trips_module.py
# Description : Liste et suivi des trajets en temps réel
# ============================================================

import customtkinter as ctk
from desktop_admin.theme.components import FluentCard, FluentButton


class TripsModule(ctk.CTkFrame):
    """Module de gestion des trajets."""
    
    def __init__(self, master, dashboard=None, user_data=None, **kwargs):
        kwargs.setdefault("fg_color", "transparent")
        super().__init__(master, **kwargs)
        
        self._trips = self._generate_mock_trips()
        
        self._build_header()
        self._build_filters()
        self._build_table()
    
    def _generate_mock_trips(self):
        trips = []
        statuses = ["proposing", "horn_pending", "payment_pending", "active", "completed", "cancelled"]
        origins = ["Libreville Centre", "Owendo", "Akanda", "PK5", "Louis", "Batie"]
        destinations = ["Awendji", "Nkoubou", "Port-Gentil", "Airport", "Franceville", "Bakoumba"]
        
        for i in range(40):
            trips.append({
                "id": f"TR{i:05d}",
                "created_at": f"2026-05-07 {10+i%12:02d}:{i%60:02d}",
                "driver": f"Driver {i % 15}",
                "origin": origins[i % 6],
                "destination": destinations[i % 6],
                "amount": [2500, 3000, 3500, 4000, 4500, 5000][i % 6],
                "seats": i % 3 + 1,
                "status": statuses[i % 6],
            })
        return trips
    
    def _build_header(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(0, 16))
        
        ctk.CTkLabel(header, text="Gestion des trajets", 
                    font=ctk.CTkFont(size=24, weight="bold")).pack(side="left")
        
        FluentButton(header, text="+ Nouveau trajet", variant="primary").pack(side="right")
    
    def _build_filters(self):
        filters = FluentCard(self, padding=16)
        filters.pack(fill="x", pady=(0, 16))
        
        date_frame = ctk.CTkFrame(filters, fg_color="transparent")
        date_frame.pack(side="left")
        
        ctk.CTkLabel(date_frame, text="Du:", font=ctk.CTkFont(size=12)).pack(side="left", padx=4)
        ctk.CTkEntry(date_frame, width=120).pack(side="left", padx=4)
        
        ctk.CTkLabel(date_frame, text="Au:", font=ctk.CTkFont(size=12)).pack(side="left", padx=16)
        ctk.CTkEntry(date_frame, width=120).pack(side="left", padx=4)
        
        ctk.CTkOptionMenu(filters, values=["Tous statuts", "active", "completed", "cancelled"], 
                         width=150).pack(side="right")
    
    def _build_table(self):
        table_card = FluentCard(self, padding=0)
        table_card.pack(fill="both", expand=True)
        
        headers = ["ID", "Date", "Chauffeur", "Départ", "Arrivée", "Montant", "Places", "Statut"]
        
        header_frame = ctk.CTkFrame(table_card, fg_color="#F5F5F5", corner_radius=0)
        header_frame.pack(fill="x")
        
        for h in headers:
            ctk.CTkLabel(header_frame, text=h, font=ctk.CTkFont(size=12, weight="bold"),
                        text_color="#6B7280", width=140).pack(side="left", padx=8, pady=12)
        
        body = ctk.CTkScrollableFrame(table_card, fg_color="transparent")
        body.pack(fill="both", expand=True)
        
        for t in self._trips:
            row = ctk.CTkFrame(body, fg_color="transparent")
            row.pack(fill="x")
            
            colors = {"active": "#009E60", "completed": "#1A3A6C", "cancelled": "#E53E3E",
                     "proposing": "#FCD116", "payment_pending": "#7C3AED", "horn_pending": "#FCD116"}
            
            ctk.CTkLabel(row, text=t["id"], font=ctk.CTkFont(size=11, weight="bold"), 
                        width=140).pack(side="left", padx=8, pady=8)
            ctk.CTkLabel(row, text=t["created_at"], width=140).pack(side="left", padx=8)
            ctk.CTkLabel(row, text=t["driver"], width=140).pack(side="left", padx=8)
            ctk.CTkLabel(row, text=t["origin"], width=140, text_color="#6B7280").pack(side="left", padx=8)
            ctk.CTkLabel(row, text=t["destination"], width=140, text_color="#6B7280").pack(side="left", padx=8)
            ctk.CTkLabel(row, text=f"{t['amount']} XAF", font=ctk.CTkFont(weight="bold"),
                        text_color="#009E60", width=140).pack(side="left", padx=8)
            ctk.CTkLabel(row, text=str(t["seats"]), width=140).pack(side="left", padx=8)
            ctk.CTkLabel(row, text=t["status"].upper(), fg_color=colors.get(t["status"], "#6B7280"),
                        text_color="white", corner_radius=4, font=ctk.CTkFont(size=10, weight="bold"),
                        padx=8, pady=2).pack(side="left", padx=8)


import random