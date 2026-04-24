# ============================================================
# Fenêtre de connexion admin — Fluent Design Windows 11
# Fichier : desktop_admin/windows/login_window.py
# Description : Layout branding gauche + formulaire droite
# ============================================================

import customtkinter as ctk
import threading


class LoginWindow(ctk.CTkFrame):
    """Fenêtre de connexion admin MobiTranz.
    
    Layout divisé en 2 panneaux :
    - Gauche (40%) : Branding avec illustration et slogan
    - Droite (60%) : Formulaire de connexion
    
    États : email+password → [2FA TOTP] → MainWindow
    """
    
    def __init__(self, master, on_success=None, **kwargs):
        kwargs.setdefault("fg_color", ("white", "#202020"))
        kwargs.setdefault("corner_radius", 0)
        super().__init__(master, **kwargs)
        
        self._on_success = on_success
        self._current_step = "credentials"
        
        # Layout 2 colonnes
        self.grid_columnconfigure(0, weight=4)
        self.grid_columnconfigure(1, weight=6)
        self.grid_rowconfigure(0, weight=1)
        
        self._build_branding_panel()
        self._build_form_panel()
    
    def _build_branding_panel(self):
        """Panneau gauche avec branding MobiTranz."""
        panel = ctk.CTkFrame(
            self,
            corner_radius=0,
            fg_color=("#1A3A6C", "#0E2244"),
        )
        panel.grid(row=0, column=0, sticky="nsew")
        
        center = ctk.CTkFrame(panel, fg_color="transparent")
        center.place(relx=0.5, rely=0.5, anchor="center")
        
        # Logo
        logo_badge = ctk.CTkLabel(
            center,
            text="🚕",
            font=ctk.CTkFont(size=72),
            width=140, height=140,
            fg_color="#FFFFFF15",
            corner_radius=32,
        )
        logo_badge.pack(pady=(0, 24))
        
        ctk.CTkLabel(
            center,
            text="MobiTranz",
            font=ctk.CTkFont(family="Segoe UI Variable Display", size=36, weight="bold"),
            text_color="white",
        ).pack()
        
        ctk.CTkLabel(
            center,
            text="Paiement Numérique pour le\nTransport Gabonais",
            font=ctk.CTkFont(family="Segoe UI Variable Text", size=16),
            text_color="#A8C4E8",
            justify="center",
        ).pack(pady=(8, 48))
        
        # Stats
        stats_frame = ctk.CTkFrame(center, fg_color="#FFFFFF0D", corner_radius=16)
        stats_frame.pack(fill="x")
        
        for label, val in [("🚗 Taxis actifs", "847"), ("💰 Trajets/jour", "3,240"), ("🔒 Sécurisé", "100%")]:
            row = ctk.CTkFrame(stats_frame, fg_color="transparent")
            row.pack(fill="x", padx=20, pady=8)
            ctk.CTkLabel(row, text=label, text_color="#A8C4E8", font=ctk.CTkFont(size=13)).pack(side="left")
            ctk.CTkLabel(row, text=val, text_color="white", font=ctk.CTkFont(size=13, weight="bold")).pack(side="right")
        
        # Footer
        ctk.CTkLabel(
            panel,
            text="🇬🇦 République Gabonaise — 2026",
            text_color="#FFFFFF55",
            font=ctk.CTkFont(size=11),
        ).place(relx=0.5, rely=0.95, anchor="center")
    
    def _build_form_panel(self):
        """Panneau droit avec formulaire."""
        panel = ctk.CTkFrame(self, corner_radius=0, fg_color=("white", "#202020"))
        panel.grid(row=0, column=1, sticky="nsew")
        
        self._form_container = ctk.CTkFrame(panel, fg_color="transparent", width=400)
        self._form_container.place(relx=0.5, rely=0.5, anchor="center")
        self._form_container.pack_propagate(False)
        
        self._build_credentials_form()
    
    def _build_credentials_form(self):
        """Formulaire email + mot de passe."""
        for widget in self._form_container.winfo_children():
            widget.destroy()
        
        from desktop_admin.theme.components import FluentEntry, FluentButton
        
        ctk.CTkLabel(
            self._form_container,
            text="Connexion",
            font=ctk.CTkFont(family="Segoe UI Variable Display", size=28, weight="bold"),
            text_color=("#1A1A1A", "white"),
            anchor="w"
        ).pack(fill="x", pady=(0, 4))
        
        ctk.CTkLabel(
            self._form_container,
            text="Accès réservé aux administrateurs MobiTranz",
            font=ctk.CTkFont(size=13),
            text_color=("#6B7280", "#9CA3AF"),
            anchor="w"
        ).pack(fill="x", pady=(0, 32))
        
        self._email_field = FluentEntry(
            self._form_container, label="Adresse email",
            placeholder="admin@mobitranz.ga", field_type="email", required=True
        )
        self._email_field.pack(fill="x", pady=(0, 16))
        
        self._password_field = FluentEntry(
            self._form_container, label="Mot de passe",
            placeholder="••••••••••••", field_type="password", required=True
        )
        self._password_field.pack(fill="x", pady=(0, 8))
        
        # Lien mot de passe oublié
        ctk.CTkButton(
            self._form_container,
            text="Mot de passe oublié ?",
            fg_color="transparent",
            hover_color="transparent",
            text_color=("#1A3A6C", "#5B85CC"),
            font=ctk.CTkFont(size=12),
            anchor="e",
        ).pack(fill="x", pady=(0, 24))
        
        self._login_btn = FluentButton(
            self._form_container,
            text="Se connecter",
            variant="primary",
            height=48,
            command=self._on_login_click
        )
        self._login_btn.pack(fill="x")
    
    def _on_login_click(self):
        """Gère la tentative de connexion."""
        email = self._email_field.get().strip()
        password = self._password_field.get().strip()
        
        if not email:
            self._email_field.set_error("L'adresse email est requise")
            return
        if not password:
            self._password_field.set_error("Le mot de passe est requis")
            return
        
        self._login_btn.set_loading(True)
        
        def do_login():
            import time
            time.sleep(1.5)
            
            mock_requires_totp = True
            
            self.after(0, lambda: self._login_btn.set_loading(False))
            
            if mock_requires_totp:
                self.after(0, self._show_totp_form)
            else:
                self.after(0, lambda: self._on_success and self._on_success({"email": email, "role": "admin"}))
        
        threading.Thread(target=do_login, daemon=True).start()
    
    def _show_totp_form(self):
        """Formulaire code 2FA TOTP."""
        for widget in self._form_container.winfo_children():
            widget.destroy()
        
        from desktop_admin.theme.components import FluentButton
        
        ctk.CTkLabel(
            self._form_container,
            text="Authentification à\ndeux facteurs",
            font=ctk.CTkFont(family="Segoe UI Variable Display", size=28, weight="bold"),
            text_color=("#1A1A1A", "white"),
            anchor="w", justify="left"
        ).pack(fill="x", pady=(0, 8))
        
        ctk.CTkLabel(
            self._form_container,
            text="Entrez le code à 6 chiffres de votre\napplication Google Authenticator",
            font=ctk.CTkFont(size=13),
            text_color=("#6B7280", "#9CA3AF"),
            anchor="w", justify="left"
        ).pack(fill="x", pady=(0, 32))
        
        self._totp_entry = ctk.CTkEntry(
            self._form_container,
            placeholder_text="000000",
            font=ctk.CTkFont(family="Cascadia Code", size=32, weight="bold"),
            height=64,
            corner_radius=12,
            justify="center",
            text_color=("#1A3A6C", "#A8C4E8"),
        )
        self._totp_entry.pack(fill="x", pady=(0, 24))
        self._totp_entry.focus()
        
        FluentButton(
            self._form_container,
            text="✓  Vérifier le code",
            variant="primary",
            height=48,
            command=self._on_totp_verify
        ).pack(fill="x", pady=(0, 12))
        
        FluentButton(
            self._form_container,
            text="← Retour",
            variant="ghost",
            height=40,
            command=self._build_credentials_form
        ).pack(fill="x")
    
    def _on_totp_verify(self):
        """Vérifie le code TOTP."""
        code = self._totp_entry.get().strip()
        if len(code) != 6 or not code.isdigit():
            self._totp_entry.configure(border_color="#E53E3E")
            return
        
        if self._on_success:
            self._on_success({"email": "admin@mobitranz.ga", "role": "admin"})