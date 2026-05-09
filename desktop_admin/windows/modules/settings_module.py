# ============================================================
# Module Paramètres — Configuration système
# Fichier : desktop_admin/windows/modules/settings_module.py
# Description : Paramètres globaux de l'application
# ============================================================

import customtkinter as ctk
from desktop_admin.theme.components import FluentCard, FluentButton, FluentEntry


class SettingsModule(ctk.CTkFrame):
    """Module de configuration système."""
    
    def __init__(self, master, dashboard=None, user_data=None, **kwargs):
        kwargs.setdefault("fg_color", "transparent")
        super().__init__(master, **kwargs)
        
        self._build_header()
        self._build_general_settings()
        self._build_payment_settings()
        self._build_zones_settings()
        self._build_notification_settings()
    
    def _build_header(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(0, 20))
        
        ctk.CTkLabel(header, text="⚙️ Paramètres système",
                    font=ctk.CTkFont(size=24, weight="bold")).pack(side="left")
        
        FluentButton(header, text="💾 Enregistrer", variant="primary", command=self._save_settings).pack(side="right")
    
    def _build_general_settings(self):
        """Paramètres généraux."""
        section = ctk.CTkFrame(self, fg_color="transparent")
        section.pack(fill="x", pady=(0, 16))
        
        ctk.CTkLabel(section, text="🏢 Configuration générale",
                    font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", pady=(0, 12))
        
        card = FluentCard(section, padding=20)
        card.pack(fill="x", pady=(0, 8))
        
        grid = ctk.CTkFrame(card, fg_color="transparent")
        grid.pack(fill="x")
        
        self._app_name = FluentEntry(grid, label="Nom de l'application", placeholder="MobiTranz", width=300)
        self._app_name.pack(side="left", padx=(0, 24))
        
        self._timezone = ctk.CTkOptionMenu(grid, values=["Africa/Libreville", "Africa/Port-Gentil", "UTC"],
                                          width=200)
        self._timezone.pack(side="left", padx=(0, 24))
        self._timezone.set("Africa/Libreville")
        
        self._debug = ctk.CTkSwitch(grid, text="Mode debug")
        self._debug.pack(side="left")
    
    def _build_payment_settings(self):
        """Paramètres de paiement."""
        section = ctk.CTkFrame(self, fg_color="transparent")
        section.pack(fill="x", pady=(0, 16))
        
        ctk.CTkLabel(section, text="💳 Configuration paiements",
                    font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", pady=(0, 12))
        
        card = FluentCard(section, padding=20)
        card.pack(fill="x", pady=(0, 8))
        
        providers = ctk.CTkFrame(card, fg_color="transparent")
        providers.pack(fill="x")
        
        ctk.CTkLabel(providers, text="Opérateurs actifs:", font=ctk.CTkFont(size=12)).pack(anchor="w", pady=(0, 8))
        
        ops = ctk.CTkFrame(providers, fg_color="transparent")
        ops.pack(fill="x")
        
        ctk.CTkCheckBox(ops, text="Airtel Money", state="checked").pack(side="left", padx=16)
        ctk.CTkCheckBox(ops, text="Moov Money", state="checked").pack(side="left", padx=16)
        ctk.CTkCheckBox(ops, text="Carte bancaire", state="checked").pack(side="left", padx=16)
        ctk.CTkCheckBox(ops, text="Paiement à l'arrivée").pack(side="left", padx=16)
        
        ctk.CTkLabel(providers, text="Frais de plateforme (%):", font=ctk.CTkFont(size=12), pady=(16, 4)).pack(anchor="w")
        
        fee_row = ctk.CTkFrame(providers, fg_color="transparent")
        fee_row.pack(fill="x")
        
        ctk.CTkEntry(fee_row, placeholder="10", width=80).pack(side="left", padx=(0, 8))
        ctk.CTkLabel(fee_row, text="% (min: 50 XAF, max: 500 XAF)", font=ctk.CTkFont(size=11), text_color="#6B7280").pack(side="left")
    
    def _build_zones_settings(self):
        """Paramètres des zones."""
        section = ctk.CTkFrame(self, fg_color="transparent")
        section.pack(fill="x", pady=(0, 16))
        
        ctk.CTkLabel(section, text="🗺️ Zones et tarifs",
                    font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", pady=(0, 12))
        
        card = FluentCard(section, padding=20)
        card.pack(fill="x", pady=(0, 8))
        
        zones = ctk.CTkFrame(card, fg_color="transparent")
        zones.pack(fill="x")
        
        ctk.CTkLabel(zones, text="Zones configurées:", font=ctk.CTkFont(size=12)).pack(anchor="w", pady=(0, 8))
        
        zone_list = [
            ("Libreville Centre", "350 XAF/km", "Actif"),
            ("Owendo", "400 XAF/km", "Actif"),
            ("Akanda", "500 XAF/km", "Actif"),
            ("PK5", "300 XAF/km", "Actif"),
            ("Port-Gentil", "600 XAF/km", "Inactif"),
        ]
        
        for zone, price, status in zone_list:
            z_row = ctk.CTkFrame(zones, fg_color="#F5F5F5", corner_radius=8)
            z_row.pack(fill="x", pady=4)
            
            ctk.CTkLabel(z_row, text=zone, font=ctk.CTkFont(size=12, weight="bold"), width=200).pack(side="left", padx=12, pady=8)
            ctk.CTkLabel(z_row, text=price, width=150).pack(side="left", padx=12)
            ctk.CTkLabel(z_row, text=status, fg_color="#009E60" if status == "Actif" else "#6B7280",
                        text_color="white", corner_radius=4, font=ctk.CTkFont(size=10),
                        padx=8, pady=2).pack(side="left", padx=12)
        
        FluentButton(zones, text="+ Ajouter zone", variant="secondary").pack(pady=(12, 0))
    
    def _build_notification_settings(self):
        """Paramètres de notification."""
        section = ctk.CTkFrame(self, fg_color="transparent")
        section.pack(fill="both", expand=True)
        
        ctk.CTkLabel(section, text="🔔 Notifications",
                    font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", pady=(0, 12))
        
        card = FluentCard(section, padding=20)
        card.pack(fill="x", pady=(0, 8))
        
        notif_row = ctk.CTkFrame(card, fg_color="transparent")
        notif_row.pack(fill="x")
        
        ctk.CTkLabel(notif_row, text="Types de notifications:", font=ctk.CTkFont(size=12)).pack(anchor="w", pady=(0, 8))
        
        notifs = [
            ("Nouvelle réservation", True),
            ("Paiement confirmé", True),
            ("Trajet terminé", True),
            ("Alerte SOS", True),
            ("Déviation de route", True),
            ("Maintenance véhicule", False),
        ]
        
        for label, checked in notifs:
            ctk.CTkCheckBox(notif_row, text=label, state="checked" if checked else "normal").pack(anchor="w", pady=2)
    
    def _save_settings(self):
        """Enregistre les paramètres."""
        print("Paramètres enregistrés!")


from desktop_admin.theme.components import FluentCard, FluentButton, FluentEntry