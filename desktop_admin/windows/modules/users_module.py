# ============================================================
# Module Utilisateurs — Gestion des utilisateurs MobiTranz
# Fichier : desktop_admin/windows/modules/users_module.py
# Description : CRUD complet avec tableau interactif et filtres
# ============================================================

import customtkinter as ctk
from datetime import datetime
from desktop_admin.theme.components import FluentCard, FluentButton, FluentEntry


class UsersModule(ctk.CTkFrame):
    """Module de gestion des utilisateurs.
    
    Fonctions :
    - Liste paginée des utilisateurs
    - Recherche multicritère
    - Filtres par rôle et statut
    - Actions (activer, suspendre, voir détails)
    """
    
    def __init__(self, master, dashboard=None, user_data=None, **kwargs):
        kwargs.setdefault("fg_color", "transparent")
        super().__init__(master, **kwargs)
        
        self._dashboard = dashboard
        self._user_data = user_data or {}
        self._users_data = self._generate_mock_users()
        
        self._build_header()
        self._build_filters()
        self._build_table()
        self._build_pagination()
    
    def _generate_mock_users(self):
        """Génère des données factices pour la démo."""
        roles = ["client", "driver", "admin", "ministry"]
        statuses = ["active", "pending", "suspended"]
        
        users = []
        for i in range(50):
            users.append({
                "id": f"user_{i:04d}",
                "phone": f"+24107{i:06d}",
                "email": f"user{i}@mobitranz.ga",
                "first_name": ["Jean", "Marie", "Paul", "Pierre", "Alice", "Claire"][i % 6],
                "last_name": ["Dupont", "Martin", "Bernard", "Petit", "Durand", "Leroy"][i % 6],
                "role": roles[i % 4],
                "status": statuses[i % 3],
                "kyc_verified": i % 3 != 1,
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
            })
        return users
    
    def _build_header(self):
        """En-tête avec titre et actions."""
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(0, 20))
        
        ctk.CTkLabel(
            header,
            text="Gestion des utilisateurs",
            font=ctk.CTkFont(family="Segoe UI Variable Display", size=24, weight="bold"),
            text_color=("#1A1A1A", "white"),
        ).pack(side="left")
        
        actions = ctk.CTkFrame(header, fg_color="transparent")
        actions.pack(side="right")
        
        FluentButton(
            actions,
            text="+ Nouvel utilisateur",
            variant="primary",
            command=self._create_user
        ).pack(side="right")
    
    def _build_filters(self):
        """Barre de filtres et recherche."""
        filters = FluentCard(self, padding=16)
        filters.pack(fill="x", pady=(0, 16))
        
        search_frame = ctk.CTkFrame(filters, fg_color="transparent")
        search_frame.pack(side="left")
        
        self._search_entry = FluentEntry(
            search_frame,
            label="Rechercher",
            placeholder="Nom, email, téléphone...",
            width=300
        )
        self._search_entry.pack(side="left", padx=(0, 16))
        
        self._role_filter = ctk.CTkOptionMenu(
            search_frame,
            values=["Tous les rôles", "client", "driver", "admin", "ministry"],
            width=160
        )
        self._role_filter.pack(side="left", padx=(0, 16))
        self._role_filter.set("Tous les rôles")
        
        self._status_filter = ctk.CTkOptionMenu(
            search_frame,
            values=["Tous les statuts", "active", "pending", "suspended"],
            width=160
        )
        self._status_filter.pack(side="left")
        self._status_filter.set("Tous les statuts")
        
        FluentButton(
            filters,
            text="🔍 Rechercher",
            variant="secondary",
            command=self._apply_filters
        ).pack(side="right")
    
    def _build_table(self):
        """Tableau des utilisateurs."""
        table_card = FluentCard(self, padding=0)
        table_card.pack(fill="both", expand=True)
        
        headers = ["ID", "Nom complet", "Téléphone", "Email", "Rôle", "Statut", "KYC", "Actions"]
        
        header_frame = ctk.CTkFrame(table_card, fg_color=("#F5F5F5", "#2C2C2C"), corner_radius=0)
        header_frame.pack(fill="x")
        
        for i, header in enumerate(headers):
            width = 120 if header == "Actions" else 150
            ctk.CTkLabel(
                header_frame,
                text=header,
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=("#6B7280", "#9CA3AF"),
                width=width,
            ).pack(side="left", padx=12, pady=12)
        
        self._table_body = ctk.CTkScrollableFrame(
            table_card,
            fg_color="transparent",
            scrollbar_button_color=("#CCCCCC", "#555555"),
        )
        self._table_body.pack(fill="both", expand=True)
        
        self._refresh_table()
    
    def _refresh_table(self, users=None):
        """Rafraîchit le tableau avec les données."""
        for widget in self._table_body.winfo_children():
            widget.destroy()
        
        users = users or self._users_data[:10]
        
        for user in users:
            row = ctk.CTkFrame(self._table_body, fg_color="transparent")
            row.pack(fill="x")
            
            role_colors = {
                "client": ("#1A3A6C", "white"),
                "driver": ("#FCD116", "#1A1A1A"),
                "admin": ("#7C3AED", "white"),
                "ministry": ("#009E60", "white"),
            }
            
            status_colors = {
                "active": ("#009E60", "white"),
                "pending": ("#FCD116", "#1A1A1A"),
                "suspended": ("#E53E3E", "white"),
            }
            
            full_name = f"{user['first_name']} {user['last_name']}"
            
            ctk.CTkLabel(
                row,
                text=user["id"],
                font=ctk.CTkFont(size=11),
                text_color=("#6B7280", "#9CA3AF"),
                width=150,
            ).pack(side="left", padx=12, pady=8)
            
            ctk.CTkLabel(
                row,
                text=full_name[:20],
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=("#1A1A1A", "white"),
                width=150,
            ).pack(side="left", padx=12)
            
            ctk.CTkLabel(
                row,
                text=user["phone"],
                font=ctk.CTkFont(size=11),
                text_color=("#6B7280", "#9CA3AF"),
                width=150,
            ).pack(side="left", padx=12)
            
            ctk.CTkLabel(
                row,
                text=user["email"][:25],
                font=ctk.CTkFont(size=11),
                text_color=("#6B7280", "#9CA3AF"),
                width=150,
            ).pack(side="left", padx=12)
            
            r_bg, r_fg = role_colors.get(user["role"], ("#6B7280", "white"))
            ctk.CTkLabel(
                row,
                text=user["role"].upper(),
                font=ctk.CTkFont(size=10, weight="bold"),
                text_color=r_fg,
                fg_color=r_bg,
                corner_radius=4,
                padx=8, pady=2
            ).pack(side="left", padx=12)
            
            s_bg, s_fg = status_colors.get(user["status"], ("#6B7280", "white"))
            ctk.CTkLabel(
                row,
                text=user["status"].upper(),
                font=ctk.CTkFont(size=10, weight="bold"),
                text_color=s_fg,
                fg_color=s_bg,
                corner_radius=4,
                padx=8, pady=2
            ).pack(side="left", padx=12)
            
            kyc_text = "✅ Vérifié" if user["kyc_verified"] else "⏳ En attente"
            kyc_color = "#009E60" if user["kyc_verified"] else "#FCD116"
            ctk.CTkLabel(
                row,
                text=kyc_text,
                font=ctk.CTkFont(size=10),
                text_color=kyc_color,
            ).pack(side="left", padx=12)
            
            actions = ctk.CTkFrame(row, fg_color="transparent", width=120)
            actions.pack(side="left", padx=8)
            
            view_btn = ctk.CTkButton(
                actions,
                text="👁️",
                width=30, height=24,
                fg_color="transparent",
                hover_color=("#E5E5E5", "#4A4A4A"),
                command=lambda u=user: self._view_user(u)
            )
            view_btn.pack(side="left", padx=2)
            
            if user["status"] == "active":
                action_btn = ctk.CTkButton(
                    actions,
                    text="🚫",
                    width=30, height=24,
                    fg_color="transparent",
                    hover_color=("#FEE2E2", "#4A2020"),
                    command=lambda u=user: self._suspend_user(u)
                )
                action_btn.pack(side="left", padx=2)
            else:
                action_btn = ctk.CTkButton(
                    actions,
                    text="✅",
                    width=30, height=24,
                    fg_color="transparent",
                    hover_color=("#DCFCE7", "#204A20"),
                    command=lambda u=user: self._activate_user(u)
                )
                action_btn.pack(side="left", padx=2)
    
    def _build_pagination(self):
        """Pagination du tableau."""
        pagination = ctk.CTkFrame(self, fg_color="transparent")
        pagination.pack(fill="x", pady=(16, 0))
        
        ctk.CTkLabel(
            pagination,
            text="Affichage 1-10 sur 50 utilisateurs",
            font=ctk.CTkFont(size=12),
            text_color=("#6B7280", "#9CA3AF"),
        ).pack(side="left")
        
        nav = ctk.CTkFrame(pagination, fg_color="transparent")
        nav.pack(side="right")
        
        for i in range(1, 6):
            btn = ctk.CTkButton(
                nav,
                text=str(i),
                width=32, height=32,
                fg_color="#1A3A6C" if i == 1 else "transparent",
                hover_color=("#E5E5E5", "#4A4A4A"),
                command=lambda p=i: self._go_to_page(p)
            )
            btn.pack(side="left", padx=2)
    
    def _apply_filters(self):
        """Applique les filtres de recherche."""
        search = self._search_entry.get().lower()
        role = self._role_filter.get()
        status = self._status_filter.get()
        
        filtered = self._users_data
        
        if search:
            filtered = [u for u in filtered if search in u["phone"] or search in u["email"] or 
                       search in u["first_name"].lower() or search in u["last_name"].lower()]
        
        if role != "Tous les rôles":
            filtered = [u for u in filtered if u["role"] == role]
        
        if status != "Tous les statuts":
            filtered = [u for u in filtered if u["status"] == status]
        
        self._refresh_table(filtered[:10])
    
    def _go_to_page(self, page):
        """Navigue vers une page."""
        start = (page - 1) * 10
        self._refresh_table(self._users_data[start:start+10])
    
    def _create_user(self):
        """Ouvre le formulaire de création."""
        pass
    
    def _view_user(self, user):
        """Affiche les détails d'un utilisateur."""
        pass
    
    def _suspend_user(self, user):
        """Suspend un utilisateur."""
        user["status"] = "suspended"
        self._refresh_table()
    
    def _activate_user(self, user):
        """Active un utilisateur."""
        user["status"] = "active"
        self._refresh_table()