# ============================================================
# Module Settings — Administration
# Fichier : desktop_admin/windows/modules/settings_module.py
# Description : Paramètres système complets avec onglets
# ============================================================

import customtkinter as ctk
from tkinter import filedialog, messagebox
from datetime import datetime
import json
import os

from desktop_admin.theme.components import FluentCard, FluentButton, FluentEntry


class SettingsModule(ctk.CTkFrame):
    """Module de paramètres système complet."""
    
    TABS = [
        ("🏠", "Général"),
        ("🔗", "API"),
        ("💳", "Paiement"),
        ("🔔", "Notifications"),
        ("🔒", "Sécurité"),
        ("⚡", "Fonctionnalités"),
        ("📍", "Zones"),
        ("👥", "Utilisateurs"),
        ("📋", "Audit"),
        ("💾", "Backup"),
    ]
    
    def __init__(self, master, user_data=None, dashboard=None, **kwargs):
        kwargs.setdefault("fg_color", "transparent")
        kwargs.pop("dashboard", None)
        kwargs.pop("user_data", None)
        super().__init__(master, **kwargs)
        
        self._user_data = user_data or {}
        self._current_tab = 0
        self._settings = self._load_settings()
        self._dirty = False
        
        self._build_header()
        self._build_tabs()
        self._build_content_area()
        self._build_footer()
        self._show_tab(0)
    
    def _load_settings(self):
        """Charge les paramètres depuis le fichier config."""
        config_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "config.json"
        )
        default_settings = {
            "general": {
                "app_name": "MobiTranz",
                "logo_path": "",
                "timezone": "Africa/Libreville",
                "language": "fr",
                "currency": "XAF",
            },
            "api": {
                "base_url": "https://api.mobitranz.ga",
                "api_key": "",
                "api_secret": "",
                "webhook_url": "",
                "timeout": 30,
            },
            "payment": {
                "moov_account": "",
                "moov_api_key": "",
                "airtel_account": "",
                "airtel_api_key": "",
                "stripe_key": "",
                "stripe_secret": "",
            },
            "notifications": {
                "fcm_server_key": "",
                "push_enabled": True,
                "sms_enabled": True,
                "email_enabled": True,
            },
            "security": {
                "2fa_required": False,
                "session_timeout": 60,
                "min_password_length": 8,
                "password_expiry_days": 90,
                "ip_whitelist": "",
            },
            "features": {
                "voice_recognition": True,
                "horn_detection": True,
                "camera_recording": True,
                "sos_alerts": True,
                "trip_tracking": True,
                "geofencing": True,
            },
            "zones": [],
            "users": [],
            "audit": [],
        }
        
        if os.path.exists(config_path):
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                    for key in default_settings:
                        if key in loaded:
                            default_settings[key].update(loaded[key])
                    return default_settings
            except Exception:
                pass
        
        return default_settings
    
    def _save_settings(self):
        """Sauvegarde les paramètres dans le fichier config."""
        config_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "config.json"
        )
        try:
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(self._settings, f, indent=2, ensure_ascii=False)
            self._dirty = False
            return True
        except Exception as e:
            messagebox.showerror("Erreur", f"Échec de sauvegarde: {e}")
            return False
    
    def _build_header(self):
        """En-tête du module."""
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(0, 16))
        
        ctk.CTkLabel(
            header,
            text="Paramètres système",
            font=ctk.CTkFont(family="Segoe UI Variable Display", size=22, weight="bold"),
            text_color=("#1A1A1A", "white"),
            anchor="w"
        ).pack(side="left")
        
        self._status_label = ctk.CTkLabel(
            header,
            text="",
            font=ctk.CTkFont(size=12),
            text_color=("#6B7280", "#9CA3AF"),
        )
        self._status_label.pack(side="right")
    
    def _build_tabs(self):
        """Barre d'onglets."""
        tabs_frame = ctk.CTkFrame(self, fg_color="transparent")
        tabs_frame.pack(fill="x", pady=(0, 16))
        
        self._tab_buttons = []
        
        for idx, (icon, label) in enumerate(self.TABS):
            btn = ctk.CTkButton(
                tabs_frame,
                text=f"  {icon}  {label}",
                anchor="w",
                height=40,
                corner_radius=8,
                fg_color="transparent",
                hover_color=("#1A3A6C", "#2D4A7C"),
                font=ctk.CTkFont(family="Segoe UI Variable Text", size=13),
                text_color=("#374151", "#D1D5DB"),
                command=lambda i=idx: self._show_tab(i)
            )
            btn.pack(side="left", padx=(0, 4))
            self._tab_buttons.append(btn)
        
        ctk.CTkFrame(tabs_frame, fg_color=("#E5E5E5", "#3D3D3D"), height=1).pack(
            fill="x", side="bottom", pady=(8, 0)
        )
    
    def _build_content_area(self):
        """Zone de contenu principale."""
        self._content_frame = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            scrollbar_button_color=("#E5E5E5", "#5A5A5A"),
        )
        self._content_frame.pack(fill="both", expand=True)
    
    def _build_footer(self):
        """Pied de page avec boutons."""
        footer = ctk.CTkFrame(self, fg_color="transparent")
        footer.pack(fill="x", pady=(16, 0))
        
        self._save_btn = FluentButton(
            footer,
            text="💾 Sauvegarder",
            variant="primary",
            height=42,
            command=self._on_save
        )
        self._save_btn.pack(side="right", padx=(8, 0))
        
        FluentButton(
            footer,
            text="🔄 Réinitialiser",
            variant="secondary",
            height=42,
            command=self._on_reset
        ).pack(side="right")
    
    def _show_tab(self, tab_index):
        """Affiche l'onglet sélectionné."""
        self._current_tab = tab_index
        
        for idx, btn in enumerate(self._tab_buttons):
            if idx == tab_index:
                btn.configure(fg_color=("#1A3A6C", "#3B5EA8"), text_color="white")
            else:
                btn.configure(fg_color="transparent", text_color=("#374151", "#D1D5DB"))
        
        for widget in self._content_frame.winfo_children():
            widget.destroy()
        
        tab_builders = [
            self._build_general_tab,
            self._build_api_tab,
            self._build_payment_tab,
            self._build_notifications_tab,
            self._build_security_tab,
            self._build_features_tab,
            self._build_zones_tab,
            self._build_users_tab,
            self._build_audit_tab,
            self._build_backup_tab,
        ]
        
        tab_builders[tab_index]()
    
    def _create_field(self, parent, label, field_type="text", key_path=None, **kwargs):
        """Crée un champ de saisie standard."""
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", pady=8)
        
        ctk.CTkLabel(
            frame,
            text=label,
            font=ctk.CTkFont(size=13),
            text_color=("#374151", "#D1D5DB"),
            width=180,
            anchor="w"
        ).pack(side="left")
        
        if field_type == "text" or field_type == "password":
            entry = ctk.CTkEntry(
                frame,
                placeholder_text=kwargs.get("placeholder", ""),
                height=40,
                corner_radius=8,
                fg_color=("white", "#2C2C2C"),
                border_color=("#E5E5E5", "#5A5A5A"),
                font=ctk.CTkFont(size=14),
            )
            entry.pack(side="left", fill="x", expand=True)
            return entry
        
        elif field_type == "select":
            combo = ctk.CTkComboBox(
                frame,
                values=kwargs.get("options", [""]),
                height=40,
                corner_radius=8,
                fg_color=("white", "#2C2C2C"),
                border_color=("#E5E5E5", "#5A5A5A"),
                font=ctk.CTkFont(size=14),
                button_color=("#1A3A6C", "#3B5EA8"),
            )
            combo.pack(side="left", fill="x", expand=True)
            return combo
        
        elif field_type == "toggle":
            switch = ctk.CTkSwitch(
                frame,
                text="",
                height=40,
                switch_width=50,
                switch_height=26,
                progress_color=("#1A3A6C", "#3B5EA8"),
            )
            switch.pack(side="left")
            return switch
        
        elif field_type == "number":
            entry = ctk.CTkEntry(
                frame,
                placeholder_text=kwargs.get("placeholder", ""),
                height=40,
                corner_radius=8,
                fg_color=("white", "#2C2C2C"),
                border_color=("#E5E5E5", "#5A5A5A"),
                font=ctk.CTkFont(size=14),
            )
            entry.pack(side="left", fill="x", expand=True)
            return entry
        
        elif field_type == "textarea":
            text = ctk.CTkTextbox(
                frame,
                height=kwargs.get("height", 80),
                corner_radius=8,
                fg_color=("white", "#2C2C2C"),
                border_color=("#E5E5E5", "#5A5A5A"),
                font=ctk.CTkFont(size=14),
            )
            text.pack(side="left", fill="x", expand=True)
            return text
        
        return None
    
    def _create_card(self, title):
        """Crée une carte Fluent."""
        card = FluentCard(self._content_frame, title=title)
        card.pack(fill="x", pady=(0, 16))
        
        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        return content
    
    def _build_general_tab(self):
        """Onglet Configuration générale."""
        content = self._create_card("Informations de l'application")
        
        field = self._create_field(content, "Nom de l'application", "text", key_path=["general", "app_name"])
        field.insert(0, self._settings["general"].get("app_name", ""))
        
        def upload_logo():
            path = filedialog.askopenfilename(
                title="Sélectionner un logo",
                filetypes=[("Images", "*.png *.jpg *.jpeg *.ico")]
            )
            if path:
                self._settings["general"]["logo_path"] = path
                self._dirty = True
                messagebox.showinfo("Succès", "Logo sélectionné avec succès!")
        
        btn = FluentButton(content, text="📁 Choisir un logo", variant="secondary", height=36, command=upload_logo)
        btn.pack(fill="x", pady=(8, 0))
        
        if self._settings["general"].get("logo_path"):
            ctk.CTkLabel(
                content,
                text=f"Sélectionné: {self._settings['general']['logo_path']}",
                font=ctk.CTkFont(size=11),
                text_color=("#6B7280", "#9CA3AF"),
            ).pack(anchor="w", pady=(4, 0))
        
        content2 = self._create_card("Localisation")
        
        field = self._create_field(content2, "Fuseau horaire", "select", key_path=["general", "timezone"],
                                options=["Africa/Libreville", "Africa/Douala", "Africa/Yaoundé", "Europe/Paris", "UTC"])
        field.set(self._settings["general"].get("timezone", "Africa/Libreville"))
        
        field = self._create_field(content2, "Langue", "select", key_path=["general", "language"],
                                options=["fr", "en", "es"])
        field.set(self._settings["general"].get("language", "fr"))
        
        field = self._create_field(content2, "Devise", "select", key_path=["general", "currency"],
                                options=["XAF", "EUR", "USD", "XOF"])
        field.set(self._settings["general"].get("currency", "XAF"))
    
    def _build_api_tab(self):
        """Onglet Configuration API."""
        content = self._create_card("API Principale")
        
        field = self._create_field(content, "URL de base", "text", key_path=["api", "base_url"],
                                placeholder="https://api.example.com")
        field.insert(0, self._settings["api"].get("base_url", ""))
        
        def mask_key(key):
            if len(key) > 4:
                return key[:2] + "●" * (len(key) - 4) + key[-2:]
            return "●" * len(key)
        
        field = self._create_field(content, "Clé API", "password", key_path=["api", "api_key"],
                                placeholder="sk_live_...")
        field.insert(0, self._settings["api"].get("api_key", ""))
        
        field = self._create_field(content, "Secret API", "password", key_path=["api", "api_secret"],
                                placeholder="Secret secret")
        field.insert(0, self._settings["api"].get("api_secret", ""))
        
        content2 = self._create_card("Webhooks")
        
        field = self._create_field(content2, "URL webhook", "text", key_path=["api", "webhook_url"],
                              placeholder="https://webhook.example.com")
        field.insert(0, self._settings["api"].get("webhook_url", ""))
        
        content3 = self._create_card("Configuration")
        
        field = self._create_field(content3, "Timeout (secondes)", "number", key_path=["api", "timeout"],
                                 placeholder="30")
        field.insert(0, str(self._settings["api"].get("timeout", 30)))
    
    def _build_payment_tab(self):
        """Onglet Paramètres de paiement."""
        content = self._create_card("MoovMoney")
        
        field = self._create_field(content, "Compte Moov", "text", key_path=["payment", "moov_account"],
                                placeholder="+237xxxxxxxxx")
        field.insert(0, self._settings["payment"].get("moov_account", ""))
        
        field = self._create_field(content, "API Key", "password", key_path=["payment", "moov_api_key"],
                                placeholder="Moov API Key")
        field.insert(0, self._settings["payment"].get("moov_api_key", ""))
        
        content2 = self._create_card("Airtel Money")
        
        field = self._create_field(content2, "Compte Airtel", "text", key_path=["payment", "airtel_account"],
                                 placeholder="+237xxxxxxxxx")
        field.insert(0, self._settings["payment"].get("airtel_account", ""))
        
        field = self._create_field(content2, "API Key", "password", key_path=["payment", "airtel_api_key"],
                                 placeholder="Airtel API Key")
        field.insert(0, self._settings["payment"].get("airtel_api_key", ""))
        
        content3 = self._create_card("Stripe")
        
        field = self._create_field(content3, "Clé publique", "text", key_path=["payment", "stripe_key"],
                                  placeholder="pk_live_...")
        field.insert(0, self._settings["payment"].get("stripe_key", ""))
        
        field = self._create_field(content3, "Clé secrète", "password", key_path=["payment", "stripe_secret"],
                                  placeholder="sk_live_...")
        field.insert(0, self._settings["payment"].get("stripe_secret", ""))
    
    def _build_notifications_tab(self):
        """Onglet Notifications."""
        content = self._create_card("Firebase Cloud Messaging")
        
        field = self._create_field(content, "FCM Server Key", "password", key_path=["notifications", "fcm_server_key"],
                                  placeholder="FCM Server Key")
        field.insert(0, self._settings["notifications"].get("fcm_server_key", ""))
        
        content2 = self._create_card("Types de notifications")
        
        switch = self._create_field(content2, "Notifications push", "toggle")
        switch.select() if self._settings["notifications"].get("push_enabled", True) else switch.deselect()
        
        switch = self._create_field(content2, "SMS", "toggle")
        switch.select() if self._settings["notifications"].get("sms_enabled", True) else switch.deselect()
        
        switch = self._create_field(content2, "Email", "toggle")
        switch.select() if self._settings["notifications"].get("email_enabled", True) else switch.deselect()
    
    def _build_security_tab(self):
        """Onglet Sécurité."""
        content = self._create_card("Authentification")
        
        switch = self._create_field(content, "2FA requis", "toggle")
        switch.select() if self._settings["security"].get("2fa_required", False) else switch.deselect()
        
        field = self._create_field(content, "Session timeout (min)", "number", key_path=["security", "session_timeout"],
                                   placeholder="60")
        field.insert(0, str(self._settings["security"].get("session_timeout", 60)))
        
        content2 = self._create_card("Politique de mot de passe")
        
        field = self._create_field(content2, "Longueur min.", "number", key_path=["security", "min_password_length"],
                                   placeholder="8")
        field.insert(0, str(self._settings["security"].get("min_password_length", 8)))
        
        field = self._create_field(content2, "Expiration (jours)", "number", key_path=["security", "password_expiry_days"],
                                 placeholder="90")
        field.insert(0, str(self._settings["security"].get("password_expiry_days", 90)))
        
        content3 = self._create_card("Liste blanche IP")
        
        field = self._create_field(content3, "Adresses IP autorisées", "textarea", key_path=["security", "ip_whitelist"],
                                 placeholder="192.168.1.0/24&#10;10.0.0.0/8",
                                 height=100)
        field.insert("1.0", self._settings["security"].get("ip_whitelist", ""))
    
    def _build_features_tab(self):
        """Onglet Fonctionnalités."""
        content = self._create_card("Fonctionnalités principales")
        
        switch = self._create_field(content, "Reconnaissance vocale", "toggle")
        switch.select() if self._settings["features"].get("voice_recognition", True) else switch.deselect()
        
        switch = self._create_field(content, "Détection de klaxon", "toggle")
        switch.select() if self._settings["features"].get("horn_detection", True) else switch.deselect()
        
        switch = self._create_field(content, "Enregistrement caméra", "toggle")
        switch.select() if self._settings["features"].get("camera_recording", True) else switch.deselect()
        
        switch = self._create_field(content, "Alertes SOS", "toggle")
        switch.select() if self._settings["features"].get("sos_alerts", True) else switch.deselect()
        
        switch = self._create_field(content, "Suivi des trajets", "toggle")
        switch.select() if self._settings["features"].get("trip_tracking", True) else switch.deselect()
        
        switch = self._create_field(content, "Géofencing", "toggle")
        switch.select() if self._settings["features"].get("geofencing", True) else switch.deselect()
    
    def _build_zones_tab(self):
        """Onglet Gestion des zones."""
        content = self._create_card("Zones de service")
        
        toolbar = ctk.CTkFrame(content, fg_color="transparent")
        toolbar.pack(fill="x", pady=(0, 12))
        
        FluentButton(
            toolbar,
            text="+ Ajouter une zone",
            variant="primary",
            height=36,
            command=self._add_zone
        ).pack(side="left")
        
        zones = self._settings.get("zones", [])
        
        if not zones:
            ctk.CTkLabel(
                content,
                text="Aucune zone définie. Cliquez sur 'Ajouter une zone' pour commencer.",
                font=ctk.CTkFont(size=13),
                text_color=("#6B7280", "#9CA3AF"),
            ).pack(pady=20)
        else:
            for idx, zone in enumerate(zones):
                zone_card = FluentCard(content, title=zone.get("name", f"Zone {idx+1}"))
                zone_card.pack(fill="x", pady=(0, 8))
                
                zone_content = ctk.CTkFrame(zone_card, fg_color="transparent")
                zone_content.pack(fill="both", expand=True, padx=16, pady=12)
                
                ctk.CTkLabel(
                    zone_content,
                    text=f"Centre: {zone.get('center', 'N/A')}",
                    font=ctk.CTkFont(size=12),
                    text_color=("#6B7280", "#9CA3AF"),
                ).pack(anchor="w")
                
                ctk.CTkLabel(
                    zone_content,
                    text=f"Rayon: {zone.get('radius', 'N/A')} km",
                    font=ctk.CTkFont(size=12),
                    text_color=("#6B7280", "#9CA3AF"),
                ).pack(anchor="w", pady=(4, 0))
                
                btn_frame = ctk.CTkFrame(zone_content, fg_color="transparent")
                btn_frame.pack(fill="x", pady=(8, 0))
                
                FluentButton(
                    btn_frame,
                    text="Modifier",
                    variant="secondary",
                    height=32,
                    command=lambda i=idx: self._edit_zone(i)
                ).pack(side="left", padx=(0, 8))
                
                FluentButton(
                    btn_frame,
                    text="Supprimer",
                    variant="danger",
                    height=32,
                    command=lambda i=idx: self._delete_zone(i)
                ).pack(side="left")
    
    def _add_zone(self):
        """Ajoute une nouvelle zone."""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Ajouter une zone")
        dialog.geometry("400x300")
        dialog.transient(self)
        dialog.grab_set()
        
        name_field = self._create_field(dialog, "Nom de la zone", "text")
        name_field.pack(fill="x", padx=20, pady=(20, 0))
        
        center_field = self._create_field(dialog, "Centre (lat,lng)", "text")
        center_field.pack(fill="x", padx=20, pady=(20, 0))
        
        radius_field = self._create_field(dialog, "Rayon (km)", "number")
        radius_field.pack(fill="x", padx=20, pady=(20, 0))
        
        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=20)
        
        def save_zone():
            if name_field.get() and center_field.get():
                self._settings.setdefault("zones", []).append({
                    "name": name_field.get(),
                    "center": center_field.get(),
                    "radius": radius_field.get() or "5",
                })
                self._dirty = True
                dialog.destroy()
                self._show_tab(6)
            else:
                messagebox.showwarning("Attention", "Veuillez remplir tous les champs obligatoires.")
        
        FluentButton(btn_frame, text="Enregistrer", variant="primary", command=save_zone).pack(side="right")
        FluentButton(btn_frame, text="Annuler", variant="secondary", command=dialog.destroy).pack(side="right", padx=(0, 8))
    
    def _edit_zone(self, index):
        """Modifie une zone."""
        messagebox.showinfo("Information", "Fonctionnalité en cours de développement.")
    
    def _delete_zone(self, index):
        """Supprime une zone."""
        if messagebox.askyesno("Confirmation", "Voulez-vous vraiment supprimer cette zone?"):
            self._settings["zones"].pop(index)
            self._dirty = True
            self._show_tab(6)
    
    def _build_users_tab(self):
        """Onglet Gestion des utilisateurs."""
        content = self._create_card("Créer un administrateur")
        
        field = self._create_field(content, "Nom d'utilisateur", "text")
        field.pack(fill="x", pady=(8, 0))
        
        field = self._create_field(content, "Email", "text")
        field.pack(fill="x", pady=(8, 0))
        
        field = self._create_field(content, "Rôle", "select", options=["Admin", "Manager", "Operator", "Viewer"])
        field.pack(fill="x", pady=(8, 0))
        
        FluentButton(
            content,
            text="Créer l'utilisateur",
            variant="primary",
            height=40,
            command=lambda: messagebox.showinfo("Succès", "Utilisateur créé avec succès!")
        ).pack(pady=(16, 0))
        
        content2 = self._create_card("Rôles")
        
        roles = [
            ("Admin", "Accès complet à toutes les fonctionnalités"),
            ("Manager", "Gestion des utilisateurs et des paramètres"),
            ("Operator", "Opérations quotidiennes"),
            ("Viewer", "Lecture seule"),
        ]
        
        for role_name, role_desc in roles:
            row = ctk.CTkFrame(content2, fg_color="transparent")
            row.pack(fill="x", pady=4)
            
            ctk.CTkLabel(
                row,
                text=role_name,
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color=("#1A1A1A", "white"),
                width=120,
                anchor="w"
            ).pack(side="left")
            
            ctk.CTkLabel(
                row,
                text=role_desc,
                font=ctk.CTkFont(size=12),
                text_color=("#6B7280", "#9CA3AF"),
                anchor="w"
            ).pack(side="left")
    
    def _build_audit_tab(self):
        """Onglet Journal d'audit."""
        content = self._create_card("Journal d'audit")
        
        toolbar = ctk.CTkFrame(content, fg_color="transparent")
        toolbar.pack(fill="x", pady=(0, 12))
        
        ctk.CTkLabel(
            toolbar,
            text="Filtres:",
            font=ctk.CTkFont(size=13),
            text_color=("#6B7280", "#9CA3AF"),
        ).pack(side="left")
        
        FluentButton(
            toolbar,
            text="📥 Exporter CSV",
            variant="secondary",
            height=36,
            command=self._export_audit
        ).pack(side="right")
        
        audit_logs = [
            ("2024-01-15 10:30:15", "admin@mobitranz.ga", "Connexion", "Succès"),
            ("2024-01-15 10:32:45", "admin@mobitranz.ga", "Modification paramètres", "Succès"),
            ("2024-01-15 11:15:00", "manager@mobitranz.ga", "Création zone", "Succès"),
            ("2024-01-15 11:45:22", "admin@mobitranz.ga", "Export données", "Succès"),
        ]
        
        header = ctk.CTkFrame(content, fg_color=("#F3F4F6", "#1F2937"))
        header.pack(fill="x")
        
        headers = [("Date", 150), ("Utilisateur", 180), ("Action", 180), ("Statut", 100)]
        
        for text, width in headers:
            ctk.CTkLabel(
                header,
                text=text,
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=("#6B7280", "#9CA3AF"),
                width=width,
                anchor="w"
            ).pack(side="left", padx=12, pady=8)
        
        for timestamp, user, action, status in audit_logs:
            row = ctk.CTkFrame(content, fg_color="transparent")
            row.pack(fill="x")
            
            ctk.CTkLabel(
                row,
                text=timestamp,
                font=ctk.CTkFont(size=12),
                text_color=("#374151", "#D1D5DB"),
                width=150,
                anchor="w"
            ).pack(side="left", padx=12)
            
            ctk.CTkLabel(
                row,
                text=user,
                font=ctk.CTkFont(size=12),
                text_color=("#374151", "#D1D5DB"),
                width=180,
                anchor="w"
            ).pack(side="left", padx=12)
            
            ctk.CTkLabel(
                row,
                text=action,
                font=ctk.CTkFont(size=12),
                text_color=("#374151", "#D1D5DB"),
                width=180,
                anchor="w"
            ).pack(side="left", padx=12)
            
            status_color = ("#009E60", "#4DC882") if status == "Succès" else ("#EF4444", "#F87171")
            ctk.CTkLabel(
                row,
                text=status,
                font=ctk.CTkFont(size=12),
                text_color=status_color,
                width=100,
                anchor="w"
            ).pack(side="left", padx=12)
    
    def _export_audit(self):
        """Exporte le journal d'audit."""
        path = filedialog.asksaveasfilename(
            title="Exporter le journal",
            defaultextension=".csv",
            filetypes=[("CSV", "*.csv")],
            initialfile=f"audit_log_{datetime.now().strftime('%Y%m%d')}"
        )
        if path:
            try:
                with open(path, "w", encoding="utf-8") as f:
                    f.write("Date,Utilisateur,Action,Statut\n")
                    f.write("2024-01-15 10:30:15,admin@mobitranz.ga,Connexion,Succès\n")
                    f.write("2024-01-15 10:32:45,admin@mobitranz.ga,Modification paramètres,Succès\n")
                messagebox.showinfo("Succès", f"Exporté vers: {path}")
            except Exception as e:
                messagebox.showerror("Erreur", f"Échec de l'export: {e}")
    
    def _build_backup_tab(self):
        """Onglet Backup et Export."""
        content = self._create_card("Sauvegarde des données")
        
        field = self._create_field(content, "Chemin de sauvegarde", "text")
        field.pack(fill="x", pady=(8, 0))
        
        FluentButton(
            content,
            text="📁 Sélectionner",
            variant="secondary",
            height=36,
        ).pack(pady=(8, 0))
        
        FluentButton(
            content,
            text="💾 Créer une sauvegarde",
            variant="primary",
            height=42,
            command=self._create_backup
        ).pack(pady=(20, 0))
        
        content2 = self._create_card("Export de données")
        
        export_options = [
            "Tous les utilisateurs",
            "Tous les chauffeurs",
            "Tous les véhicules",
            "Tous les trajets",
            "Tous les incidents",
            "Tous les transactions",
        ]
        
        for option in export_options:
            btn = FluentButton(
                content2,
                text=f"📥 Exporter {option}",
                variant="secondary",
                height=36,
                command=lambda o=option: self._export_data(o)
            )
            btn.pack(fill="x", pady=4)
        
        content3 = self._create_card("Paramètres d'export")
        
        switch = self._create_field(content3, "Inclure les fichiers médias", "toggle")
        switch.select()
    
    def _create_backup(self):
        """Crée une sauvegarde."""
        messagebox.showinfo("Information", "Fonctionnalité en cours de développement.")
    
    def _export_data(self, data_type):
        """Exporte les données."""
        path = filedialog.asksaveasfilename(
            title=f"Exporter {data_type}",
            defaultextension=".json",
            filetypes=[("JSON", "*.json"), ("CSV", "*.csv")],
        )
        if path:
            try:
                with open(path, "w", encoding="utf-8") as f:
                    json.dump({data_type: []}, f, indent=2)
                messagebox.showinfo("Succès", f"Données exportées vers: {path}")
            except Exception as e:
                messagebox.showerror("Erreur", f"Échec de l'export: {e}")
    
    def _on_save(self):
        """Enregistre les paramètres."""
        if self._dirty:
            if self._save_settings():
                messagebox.showinfo("Succès", "Paramètres enregistrés avec succès!")
                self._status_label.configure(text="✓ Modifications enregistrées")
            else:
                messagebox.showerror("Erreur", "Échec de l'enregistrement des paramètres.")
        else:
            messagebox.showinfo("Information", "Aucune modification à enregistrer.")
    
    def _on_reset(self):
        """Réinitialise les paramètres."""
        if messagebox.askyesno("Confirmation", "Voulez-vous vraiment réinitialiser tous les paramètres?"):
            self._settings = self._load_settings()
            self._show_tab(self._current_tab)
            self._status_label.configure(text="✓ Paramètres réinitialisés")