# ============================================================
# Fenetre de connexion admin — Fluent Design Windows 11
# Fichier : desktop_admin/windows/login_window.py
# Description : Layout branding gauche + formulaire droite
# ============================================================

import customtkinter as ctk
import os
import sys

project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, project_root)

from shared.api_client import TokenStorage
from desktop_admin.windows.theme.ui_theme import UITheme, get_palette, font, title_font, body_font


class LoginWindow(ctk.CTkFrame):
    """Fenetre de connexion admin MobiTranz.
    
    Layout divise en 2 panneaux :
    - Gauche (40%) : Branding avec illustration et slogan
    - Droite (60%) : Formulaire de connexion
    
    États : email+password -> MainWindow
    """
    
    def __init__(self, master, on_success=None, **kwargs):
        kwargs.setdefault("fg_color", "transparent")
        kwargs.setdefault("corner_radius", 0)
        super().__init__(master, **kwargs)
        
        self._on_success = on_success
        self._initialize_theme()
        
        self.grid_columnconfigure(0, weight=4)
        self.grid_columnconfigure(1, weight=6)
        self.grid_rowconfigure(0, weight=1)
        
        self._build_branding_panel()
        self._build_form_panel()
    
    def _initialize_theme(self):
        """Initialize theme and appearance mode."""
        try:
            ctk.set_appearance_mode("Dark")
            try:
                ctk.set_default_color_theme("dark-blue")
            except Exception:
                pass
        except Exception:
            pass
        self._pal = get_palette()
    
    def _get_colors(self):
        """Get current theme colors."""
        return get_palette()
    
    def _build_branding_panel(self):
        """Panneau gauche avec branding MobiTranz."""
        pal = self._get_colors()
        
        panel = ctk.CTkFrame(self, corner_radius=0, fg_color=("#1A3A6C", "#0E2244"))
        panel.grid(row=0, column=0, sticky="nsew")
        
        center = ctk.CTkFrame(panel, fg_color="transparent")
        center.place(relx=0.5, rely=0.5, anchor="center")
        
        logo_badge = ctk.CTkLabel(
            center, text="🚕", font=ctk.CTkFont(size=72),
            width=140, height=140, fg_color="#FFFFFF", corner_radius=32,
        )
        logo_badge.pack(pady=(0, 24))
        
        ctk.CTkLabel(
            center, text="MobiTranz",
            font=title_font(36), text_color="white",
        ).pack()
        
        ctk.CTkLabel(
            center, text="Paiement Numerique pour le\nTransport Gabonais",
            font=body_font(16), text_color="#A8C4E8",
            justify="center",
        ).pack(pady=(8, 48))
        
        stats_frame = ctk.CTkFrame(center, fg_color="#FFFFFF", corner_radius=16)
        stats_frame.pack(fill="x")
        
        for label, val in [("🚗 Taxis actifs", "847"), ("💰 Trajets/jour", "3,240"), ("🔒 Securise", "100%")]:
            row = ctk.CTkFrame(stats_frame, fg_color="transparent")
            row.pack(fill="x", padx=20, pady=8)
            ctk.CTkLabel(row, text=label, text_color="#A8C4E8", font=body_font(13)).pack(side="left")
            ctk.CTkLabel(row, text=val, text_color="white", font=body_font(13, "bold")).pack(side="right")
        
        ctk.CTkLabel(
            panel, text="🇬🇦 Republique Gabonaise — 2026",
            text_color="#AAAAAA", font=body_font(11),
        ).place(relx=0.5, rely=0.95, anchor="center")
    
    def _build_form_panel(self):
        """Panneau droit avec formulaire."""
        pal = self._get_colors()
        fg = pal["surface"]
        tc = pal["text"]
        tc_m = pal["text_secondary"]
        primary = pal["primary"]
        
        panel = ctk.CTkFrame(self, corner_radius=0, fg_color=(fg, "#1F2937"))
        panel.grid(row=0, column=1, sticky="nsew")
        
        container = ctk.CTkFrame(panel, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=60)
        
        ctk.CTkLabel(
            container, text="Connexion",
            font=title_font(32), text_color=tc, anchor="w"
        ).pack(fill="x", pady=(60, 4))
        
        ctk.CTkLabel(
            container, text="Acces reserve aux administrateurs MobiTranz",
            font=body_font(14), text_color=tc_m, anchor="w"
        ).pack(fill="x", pady=(0, 32))
        
        ctk.CTkLabel(
            container, text="Adresse email",
            font=body_font(13), text_color=tc_m, anchor="w"
        ).pack(fill="x", pady=(0, 4))
        
        self._email_field = ctk.CTkEntry(
            container, placeholder_text="admin@mobitranz.ga",
            height=46, font=body_font(15), fg_color=pal["input_bg"],
            border_color=pal["input_border"], text_color=tc,
        )
        self._email_field.pack(fill="x", pady=(0, 20))
        
        ctk.CTkLabel(
            container, text="Mot de passe",
            font=body_font(13), text_color=tc_m, anchor="w"
        ).pack(fill="x", pady=(0, 4))
        
        self._password_field = ctk.CTkEntry(
            container, placeholder_text="••••••••••••",
            height=46, show="●", font=body_font(15),
            fg_color=pal["input_bg"], border_color=pal["input_border"], text_color=tc,
        )
        self._password_field.pack(fill="x", pady=(0, 8))
        
        self._theme_btn = ctk.CTkButton(
            container, text="🌙 Mode sombre / ☀️ Mode clair",
            fg_color="transparent", text_color=primary,
            hover_color=pal["surface_hover"], border_width=1,
            border_color=pal["input_border"], height=36,
            font=body_font(12), command=self._toggle_theme
        )
        self._theme_btn.pack(fill="x", pady=(0, 16))
        
        ctk.CTkButton(
            container, text="Mot de passe oublie ?",
            fg_color="transparent", text_color=("#1A3A6C", "#5B85CC"),
            font=body_font(13), anchor="e",
        ).pack(fill="x", pady=(0, 16))
        
        self._login_btn = ctk.CTkButton(
            container, text="Se connecter",
            fg_color=primary, hover_color=pal["primary_hover"],
            text_color="white", height=50,
            font=body_font(13, weight="bold"), command=self._on_login_click
        )
        self._login_btn.pack(fill="x")
        
        self._password_field.bind("<Return>", lambda e: self._on_login_click())
    
    def _toggle_theme(self):
        """Toggle between light and dark mode."""
        new_mode = UITheme.toggle_mode()
        self._pal = get_palette()
        self._refresh_form_panel()
    
    def _refresh_form_panel(self):
        """Refresh form panel colors."""
        pal = self._get_colors()
        if hasattr(self, '_theme_btn'):
            mode = UITheme.get_mode()
            self._theme_btn.configure(
                text="☀️ Passer en mode clair" if mode == "Dark" else "🌙 Passer en mode sombre"
            )
    
    def _on_login_click(self):
        """Gere la tentative de connexion (mode mock pour test)."""
        email = self._email_field.get().strip()
        password = self._password_field.get().strip()
        pal = self._get_colors()
        
        if not email:
            self._email_field.configure(border_color=pal["danger"])
            return
        if not password:
            self._password_field.configure(border_color=pal["danger"])
            return
        
        self._login_btn.configure(state="disabled", text="Connexion...")
        
        import time
        time.sleep(0.8)
        
        mock_token = "mock_access_token_" + str(int(time.time()))
        
        TokenStorage.store(
            access_token=mock_token,
            refresh_token="mock_refresh_token",
            expires_in_seconds=900,
        )
        
        if self._on_success:
            self._on_success({"email": email, "role": "admin", "name": "Admin MobiTranz"})