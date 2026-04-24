# ============================================================
# Module Users — Administration
# Fichier : desktop_admin/windows/modules/users_module.py
# Description : CRUD utilisateurs, KYC, suspension
# ============================================================

import customtkinter as ctk
from desktop_admin.theme.components import FluentCard, FluentButton


class UsersModule(ctk.CTkFrame):
    """Module de gestion des utilisateurs."""
    
    def __init__(self, master, user_data=None, **kwargs):
        kwargs.setdefault("fg_color", "transparent")
        super().__init__(master, **kwargs)
        
        self._user_data = user_data or {}
        
        self._build_header()
        self._build_content()
    
    def _build_header(self):
        """En-tête du module."""
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(0, 16))
        
        ctk.CTkLabel(
            header,
            text="Gestion des utilisateurs",
            font=ctk.CTkFont(family="Segoe UI Variable Display", size=22, weight="bold"),
            text_color=("#1A1A1A", "white"),
            anchor="w"
        ).pack(side="left")
        
        right = ctk.CTkFrame(header, fg_color="transparent")
        right.pack(side="right")
        
        FluentButton(
            right, text="+ Ajouter utilisateur",
            variant="primary", height=36,
        ).pack(side="right")
    
    def _build_content(self):
        """Contenu du module."""
        card = FluentCard(self, title="Liste des utilisateurs")
        card.pack(fill="both", expand=True, pady=(0, 16))
        
        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # En-têtes du tableau
        headers = ["ID", "Téléphone", "Email", "Rôle", "Statut", "Actions"]
        cols = [2, 3, 3, 1, 1, 1]
        
        header_frame = ctk.CTkFrame(content, fg_color=("#F3F4F6", "#2D3748"))
        header_frame.pack(fill="x", pady=(0, 8))
        
        for i, (h, w) in enumerate(zip(headers, cols)):
            ctk.CTkLabel(
                header_frame, text=h,
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=("#6B7280", "#9CA3AF"),
                width=w*80,
            ).pack(side="left", padx=8, pady=8)
        
        # Données simulées
        users = [
            ("usr_001", "+241 05 00 00 01", "john@test.com", "CLIENT", "ACTIF", "👁️ 🚫"),
            ("usr_002", "+241 05 00 00 02", "alice@test.com", "DRIVER", "ACTIF", "👁️ 🚫"),
            ("usr_003", "+241 05 00 00 03", "bob@test.com", "ADMIN", "SUSPENDU", "👁️ ✓"),
        ]
        
        for user in users:
            row = ctk.CTkFrame(content, fg_color=("white", "#2C2C2C"), corner_radius=8)
            row.pack(fill="x", pady=2)
            
            for i, (cell, w) in enumerate(zip(user, cols)):
                ctk.CTkLabel(
                    row, text=cell,
                    font=ctk.CTkFont(size=12),
                    text_color=("#374151", "#D1D5DB"),
                    width=w*80,
                ).pack(side="left", padx=8, pady=10)