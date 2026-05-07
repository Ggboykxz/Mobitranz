# ============================================================
# Module Incidents — Gestion des alertes et incidents
# Fichier : desktop_admin/windows/modules/incidents_module.py
# Description : Suivi des incidents et escalade aux autorités
# ============================================================

import customtkinter as ctk
from desktop_admin.theme.components import FluentCard, FluentButton


class IncidentsModule(ctk.CTkFrame):
    """Module de gestion des incidents."""
    
    def __init__(self, master, dashboard=None, user_data=None, **kwargs):
        kwargs.setdefault("fg_color", "transparent")
        super().__init__(master, **kwargs)
        
        self._incidents = self._generate_mock_incidents()
        
        self._build_header()
        self._build_alert_panel()
        self._build_table()
    
    def _generate_mock_incidents(self):
        incidents = []
        types = ["sos", "accident", "dispute", "theft", "harassment", "other"]
        statuses = ["pending", "acknowledged", "escalated", "resolved", "closed"]
        
        for i in range(20):
            incidents.append({
                "id": f"INC{i:06d}",
                "created_at": f"2026-05-07 {10+i%12:02d}:{i%60:02d}",
                "type": types[i % 6],
                "status": statuses[i % 5],
                "trip_id": f"TR{i:05d}",
                "reporter": f"+24107{i:06d}",
                "description": ["Déviation suspecte", "Accident de circulation", "Refus de payer", 
                              "Objet oublié", "Harcèlement", "Autre"][i % 6],
                "location": f"Lat: 0.4{i}, Lon: 9.4{i}",
                "escalated_to": "Ministère Intérieur" if i % 5 == 2 else None,
            })
        return incidents
    
    def _build_header(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(0, 16))
        
        ctk.CTkLabel(header, text="Gestion des incidents et alertes",
                    font=ctk.CTkFont(size=24, weight="bold")).pack(side="left")
        
        FluentButton(header, text="🚨 Nouvelle alerte", variant="danger").pack(side="right")
    
    def _build_alert_panel(self):
        """Panneau d'alertes actives importantes."""
        alert_frame = ctk.CTkFrame(self, fg_color="transparent")
        alert_frame.pack(fill="x", pady=(0, 16))
        
        active_alerts = [i for i in self._incidents if i["status"] in ["pending", "acknowledged", "escalated"]]
        
        if active_alerts:
            for alert in active_alerts[:3]:
                card = FluentCard(alert_frame, padding=12)
                card.pack(side="left", padx=(0, 12), fill="both", expand=True)
                
                icon = "🚨" if alert["type"] == "sos" else "⚠️"
                
                top = ctk.CTkFrame(card, fg_color="transparent")
                top.pack(fill="x")
                
                ctk.CTkLabel(top, text=f"{icon} {alert['type'].upper()}", font=ctk.CTkFont(size=14, weight="bold"),
                            text_color="#E53E3E").pack(side="left")
                ctk.CTkLabel(top, text=alert["created_at"], font=ctk.CTkFont(size=10),
                            text_color="#6B7280").pack(side="right")
                
                ctk.CTkLabel(card, text=f"Trajet: {alert['trip_id']}", font=ctk.CTkFont(size=12)).pack(anchor="w")
                ctk.CTkLabel(card, text=f"Signalé par: {alert['reporter']}", font=ctk.CTkFont(size=11),
                            text_color="#6B7280").pack(anchor="w")
                
                actions = ctk.CTkFrame(card, fg_color="transparent")
                actions.pack(fill="x", pady=(8, 0))
                
                FluentButton(actions, text="Traiter", variant="success", width=80).pack(side="left", padx=4)
                if not alert["escalated_to"]:
                    FluentButton(actions, text="Escaler", variant="warning", width=80).pack(side="left", padx=4)
    
    def _build_table(self):
        table_card = FluentCard(self, padding=0)
        table_card.pack(fill="both", expand=True)
        
        headers = ["ID", "Date", "Type", "Trajet", "Signalé par", "Description", "Statut", "Actions"]
        
        header_frame = ctk.CTkFrame(table_card, fg_color="#F5F5F5", corner_radius=0)
        header_frame.pack(fill="x")
        
        for h in headers:
            ctk.CTkLabel(header_frame, text=h, font=ctk.CTkFont(size=12, weight="bold"),
                        text_color="#6B7280", width=130).pack(side="left", padx=8, pady=12)
        
        body = ctk.CTkScrollableFrame(table_card, fg_color="transparent")
        body.pack(fill="both", expand=True)
        
        for inc in self._incidents:
            row = ctk.CTkFrame(body, fg_color="transparent")
            row.pack(fill="x")
            
            type_colors = {"sos": "#E53E3E", "accident": "#FCD116", "dispute": "#7C3AED",
                          "theft": "#E53E3E", "harassment": "#E53E3E", "other": "#6B7280"}
            status_colors = {"pending": "#FCD116", "acknowledged": "#1A3A6C", "escalated": "#E53E3E",
                           "resolved": "#009E60", "closed": "#6B7280"}
            
            ctk.CTkLabel(row, text=inc["id"], font=ctk.CTkFont(size=11, weight="bold"),
                        width=130).pack(side="left", padx=8, pady=8)
            ctk.CTkLabel(row, text=inc["created_at"], width=130).pack(side="left", padx=8)
            ctk.CTkLabel(row, text=inc["type"].upper(), fg_color=type_colors.get(inc["type"]),
                        text_color="white", corner_radius=4, font=ctk.CTkFont(size=10, weight="bold"),
                        padx=8, pady=2).pack(side="left", padx=8)
            ctk.CTkLabel(row, text=inc["trip_id"], width=130).pack(side="left", padx=8)
            ctk.CTkLabel(row, text=inc["reporter"], width=130, text_color="#6B7280").pack(side="left", padx=8)
            ctk.CTkLabel(row, text=inc["description"][:20], width=130, text_color="#6B7280").pack(side="left", padx=8)
            ctk.CTkLabel(row, text=inc["status"].upper(), fg_color=status_colors.get(inc["status"]),
                        text_color="white", corner_radius=4, font=ctk.CTkFont(size=10, weight="bold"),
                        padx=8, pady=2).pack(side="left", padx=8)
            
            FluentButton(ctk.CTkFrame(row, fg_color="transparent"), text="👁️", width=28, height=24,
                        fg_color="transparent").pack(side="left", padx=4)
            if inc["escalated_to"]:
                ctk.CTkLabel(row, text="📤", width=28).pack(side="left", padx=4)
            else:
                FluentButton(ctk.CTkFrame(row, fg_color="transparent"), text="📤", width=28, height=24,
                            fg_color="transparent").pack(side="left", padx=4)


import random