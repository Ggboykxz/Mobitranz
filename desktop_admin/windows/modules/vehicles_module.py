# ============================================================
# Module Véhicules — Gestion des véhicules MobiTranz
# Fichier : desktop_admin/windows/modules/vehicles_module.py
# Description : Gestion du parc vehicular avec statut et caméra
# ============================================================

import customtkinter as ctk
from desktop_admin.theme.components import FluentCard, FluentButton


class VehiclesModule(ctk.CTkFrame):
    """Module de gestion des véhicules."""
    
    def __init__(self, master, dashboard=None, user_data=None, **kwargs):
        kwargs.setdefault("fg_color", "transparent")
        super().__init__(master, **kwargs)
        
        self._vehicles = self._generate_mock_vehicles()
        
        self._build_header()
        self._build_stats()
        self._build_table()
    
    def _generate_mock_vehicles(self):
        vehicles = []
        brands = ["Toyota", "Hyundai", "Kia", "Nissan", "Ford"]
        models = ["Corolla", "Tucson", "Sportage", "Navara", "Ranger"]
        colors = ["Blanc", "Noir", "Gris", "Bleu", "Rouge"]
        
        for i in range(25):
            vehicles.append({
                "id": f"veh_{i:04d}",
                "plate": f"T{i:04d}G",
                "brand": brands[i % 5],
                "model": models[i % 5],
                "color": colors[i % 5],
                "year": 2020 + (i % 4),
                "total_seats": 4,
                "available_seats": i % 4 + 1,
                "status": ["active", "maintenance", "inactive"][i % 3],
                "camera_enabled": i % 2 == 0,
                "driver": f"Driver {i}" if i % 3 != 2 else None,
            })
        return vehicles
    
    def _build_header(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(0, 16))
        
        ctk.CTkLabel(
            header,
            text="Gestion des véhicules",
            font=ctk.CTkFont(family="Segoe UI Variable Display", size=24, weight="bold"),
        ).pack(side="left")
        
        FluentButton(
            header,
            text="+ Ajouter véhicule",
            variant="primary",
            command=self._add_vehicle
        ).pack(side="right")
    
    def _build_stats(self):
        stats = ctk.CTkFrame(self, fg_color="transparent")
        stats.pack(fill="x", pady=(0, 16))
        
        items = [
            ("total", "25", "Total véhicules", "#1A3A6C"),
            ("active", "18", "En service", "#009E60"),
            ("maintenance", "4", "Maintenance", "#FCD116"),
            ("inactive", "3", "Inactifs", "#6B7280"),
        ]
        
        for _, value, label, color in items:
            card = FluentCard(stats, padding=16)
            card.pack(side="left", padx=(0, 12), fill="both", expand=True)
            
            ctk.CTkLabel(card, text=value, font=ctk.CTkFont(size=28, weight="bold")).pack()
            ctk.CTkLabel(card, text=label, font=ctk.CTkFont(size=12), text_color="#6B7280").pack()
    
    def _build_table(self):
        table_card = FluentCard(self, padding=0)
        table_card.pack(fill="both", expand=True)
        
        headers = ["Plaque", "Marque/Modèle", "Année", "Places", "Chauffeur", "Caméra", "Statut", "Actions"]
        
        header_frame = ctk.CTkFrame(table_card, fg_color="#F5F5F5", corner_radius=0)
        header_frame.pack(fill="x")
        
        for h in headers:
            ctk.CTkLabel(header_frame, text=h, font=ctk.CTkFont(size=12, weight="bold"), 
                        text_color="#6B7280", width=130).pack(side="left", padx=8, pady=12)
        
        body = ctk.CTkScrollableFrame(table_card, fg_color="transparent")
        body.pack(fill="both", expand=True)
        
        for v in self._vehicles:
            row = ctk.CTkFrame(body, fg_color="transparent")
            row.pack(fill="x")
            
            ctk.CTkLabel(row, text=v["plate"], font=ctk.CTkFont(size=12, weight="bold"), 
                        width=130).pack(side="left", padx=8, pady=8)
            
            ctk.CTkLabel(row, text=f"{v['brand']} {v['model']}", width=130).pack(side="left", padx=8)
            
            ctk.CTkLabel(row, text=str(v["year"]), width=130).pack(side="left", padx=8)
            
            ctk.CTkLabel(row, text=f"{v['available_seats']}/{v['total_seats']}", 
                        width=130, text_color="#009E60" if v['available_seats'] > 0 else "#E53E3E").pack(side="left", padx=8)
            
            ctk.CTkLabel(row, text=v["driver"] or "—", width=130).pack(side="left", padx=8)
            
            cam = "✅ Active" if v["camera_enabled"] else "❌ Inactive"
            ctk.CTkLabel(row, text=cam, text_color="#009E60" if v["camera_enabled"] else "#6B7280", 
                        width=130).pack(side="left", padx=8)
            
            colors = {"active": "#009E60", "maintenance": "#FCD116", "inactive": "#6B7280"}
            ctk.CTkLabel(row, text=v["status"].upper(), fg_color=colors.get(v["status"]), 
                        text_color="white", corner_radius=4, font=ctk.CTkFont(size=10, weight="bold"),
                        padx=8, pady=2).pack(side="left", padx=8)
            
            FluentButton(ctk.CTkFrame(row, fg_color="transparent"), text="📷", width=30, height=24,
                         fg_color="transparent").pack(side="left", padx=4)
            FluentButton(ctk.CTkFrame(row, fg_color="transparent"), text="📍", width=30, height=24,
                         fg_color="transparent").pack(side="left", padx=4)
    
    def _add_vehicle(self):
        pass


import random