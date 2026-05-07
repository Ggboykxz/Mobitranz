# ============================================================
# Module Audit & Logs — Sécurité et traçabilité
# Fichier : desktop_admin/windows/modules/audit_module.py
# Description : Journalisation des actions et sécurité
# ============================================================

import customtkinter as ctk
from datetime import datetime
from desktop_admin.theme.components import FluentCard, FluentButton


class AuditModule(ctk.CTkFrame):
    """Module d'audit et sécurité."""
    
    def __init__(self, master, dashboard=None, user_data=None, **kwargs):
        kwargs.setdefault("fg_color", "transparent")
        super().__init__(master, **kwargs)
        
        self._build_header()
        self._build_security_overview()
        self._build_access_logs()
        self._build_failed_logins()
    
    def _build_header(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(0, 20))
        
        ctk.CTkLabel(header, text="🔒 Sécurité et Audit",
                    font=ctk.CTkFont(size=24, weight="bold")).pack(side="left")
        
        FluentButton(header, text="📥 Exporter logs", variant="secondary").pack(side="right")
    
    def _build_security_overview(self):
        """Vue d'ensemble de la sécurité."""
        overview = ctk.CTkFrame(self, fg_color="transparent")
        overview.pack(fill="x", pady=(0, 16))
        
        stats = [
            ("✅", "128", "Connexions aujourd'hui", "#009E60"),
            ("⚠️", "3", "Tentatives bloquées", "#E53E3E"),
            ("🔐", "12", "Sessions actives", "#1A3A6C"),
            ("👥", "5", "Admins en ligne", "#7C3AED"),
        ]
        
        for icon, value, label, color in stats:
            card = FluentCard(overview, padding=16)
            card.pack(side="left", padx=(0, 12), fill="both", expand=True)
            
            ctk.CTkLabel(card, text=icon, font=ctk.CTkFont(size=20)).pack()
            ctk.CTkLabel(card, text=value, font=ctk.CTkFont(size=28, weight="bold"),
                        text_color=color).pack()
            ctk.CTkLabel(card, text=label, font=ctk.CTkFont(size=11),
                        text_color="#6B7280").pack()
    
    def _build_access_logs(self):
        """Journal des accès."""
        section = ctk.CTkFrame(self, fg_color="transparent")
        section.pack(fill="x", pady=(0, 16))
        
        ctk.CTkLabel(section, text="📋 Journal des accès",
                    font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", pady=(0, 12))
        
        filters = FluentCard(section, padding=12)
        filters.pack(fill="x", pady=(0, 8))
        
        ctk.CTkEntry(filters, placeholder="Rechercher...", width=200).pack(side="left", padx=(0, 8))
        ctk.CTkOptionMenu(filters, values=["Toutes actions", "LOGIN", "LOGOUT", "CREATE", "UPDATE", "DELETE"],
                         width=150).pack(side="left", padx=(0, 8))
        ctk.CTkOptionMenu(filters, values=["Tous utilisateurs", "admin", "driver", "client"],
                         width=150).pack(side="left")
        
        table_card = FluentCard(section, padding=0)
        table_card.pack(fill="both", expand=True)
        
        headers = ["Horodatage", "Utilisateur", "Action", "Ressource", "IP", "Résultat"]
        
        header_frame = ctk.CTkFrame(table_card, fg_color="#F5F5F5", corner_radius=0)
        header_frame.pack(fill="x")
        
        for h in headers:
            ctk.CTkLabel(header_frame, text=h, font=ctk.CTkFont(size=12, weight="bold"),
                        text_color="#6B7280", width=140).pack(side="left", padx=8, pady=10)
        
        body = ctk.CTkScrollableFrame(table_card, fg_color="transparent")
        body.pack(fill="both", expand=True)
        
        actions = ["LOGIN", "LOGOUT", "CREATE_USER", "UPDATE_TRIP", "DELETE_PAYMENT", "VIEW_RECORDING"]
        resources = ["auth", "trips:TR00012", "users:user_0042", "payments:TXN123456", "recordings:cam_01"]
        users = ["admin@mobitranz.ga", "driver_01", "client_05", "admin@mobitranz.ga"]
        ips = ["192.168.1.45", "192.168.1.78", "192.168.1.102", "192.168.1.45"]
        results = ["success", "success", "success", "failure", "success", "success"]
        
        for i in range(15):
            row = ctk.CTkFrame(body, fg_color="transparent")
            row.pack(fill="x")
            
            result_colors = {"success": "#009E60", "failure": "#E53E3E"}
            
            ctk.CTkLabel(row, text=f"2026-05-07 {10+i%12:02d}:{i%60:02d}:00", width=140, font=ctk.CTkFont(size=10)).pack(side="left", padx=8, pady=6)
            ctk.CTkLabel(row, text=users[i % 4], width=140, font=ctk.CTkFont(size=10)).pack(side="left", padx=8)
            ctk.CTkLabel(row, text=actions[i % 6], width=140, font=ctk.CTkFont(size=10, weight="bold"), text_color="#1A3A6C").pack(side="left", padx=8)
            ctk.CTkLabel(row, text=resources[i % 5], width=140, font=ctk.CTkFont(size=10)).pack(side="left", padx=8)
            ctk.CTkLabel(row, text=ips[i % 4], width=140, font=ctk.CTkFont(size=10), text_color="#6B7280").pack(side="left", padx=8)
            ctk.CTkLabel(row, text=results[i % 4].upper(), fg_color=result_colors.get(results[i % 4]),
                        text_color="white", corner_radius=4, font=ctk.CTkFont(size=10, weight="bold"),
                        padx=8, pady=2).pack(side="left", padx=8)
    
    def _build_failed_logins(self):
        """Tentatives de connexion échouées."""
        section = ctk.CTkFrame(self, fg_color="transparent")
        section.pack(fill="both", expand=True)
        
        ctk.CTkLabel(section, text="⚠️ Alertes de sécurité",
                    font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", pady=(0, 12))
        
        alerts = [
            ("🔴", "admin@mobitranz.ga", "3 tentatives échouées", "Il y a 15 min", "Bloquer IP"),
            ("🟡", "+24107XXX1234", "Compte verrouillé", "Il y a 1h", "Déverrouiller"),
            ("🔴", "driver_08", "Accès camera suspect", "Il y a 2h", "Investiguer"),
        ]
        
        for icon, user, desc, time, action in alerts:
            card = FluentCard(section, padding=16)
            card.pack(fill="x", pady=(0, 8))
            
            row = ctk.CTkFrame(card, fg_color="transparent")
            row.pack(fill="x")
            
            ctk.CTkLabel(row, text=icon, font=ctk.CTkFont(size=20)).pack(side="left", padx=(0, 12))
            
            info = ctk.CTkFrame(row, fg_color="transparent")
            info.pack(side="left", fill="x", expand=True)
            
            ctk.CTkLabel(info, text=user, font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w")
            ctk.CTkLabel(info, text=f"{desc} • {time}", font=ctk.CTkFont(size=11), text_color="#6B7280").pack(anchor="w")
            
            FluentButton(row, text=action, variant="danger" if "Bloquer" in action else "secondary").pack(side="right")