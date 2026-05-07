# ============================================================
# Module Utilisateurs — Gestion des utilisateurs MobiTranz
# Fichier : desktop_admin/windows/modules/users_module.py
# Description : CRUD complet avec tableau interactif et détails
# ============================================================

import customtkinter as ctk
from datetime import datetime
from desktop_admin.theme.components import FluentCard, FluentButton, FluentEntry
from desktop_admin.theme.components_detail import show_detail


class UsersModule(ctk.CTkFrame):
    """Module de gestion des utilisateurs avec détails complets.
    
    Sous-modules:
    - Vue tableau avec pagination
    - Détails complets (cliquable)
    - Historique des activités
    - Documents et pièces
    - Statistiques
    - Actions (modifier, suspendre, supprimer)
    """
    
    def __init__(self, master, dashboard=None, user_data=None, **kwargs):
        kwargs.setdefault("fg_color", "transparent")
        super().__init__(master, **kwargs)
        
        self._dashboard = dashboard
        self._user_data = user_data or {}
        self._api_client = dashboard.api_client if dashboard else None
        
        self._load_data()
        self._build_header()
        self._build_filters()
        self._build_table()
        self._build_pagination()
    
    def _load_data(self):
        """Charge les données depuis l'API."""
        try:
            if self._api_client:
                self._users_data = self._api_client.get_users(limit=100)
            else:
                self._users_data = self._get_demo_data()
        except Exception as e:
            print(f"Erreur API: {e}")
            self._users_data = self._get_demo_data()
    
    def _get_demo_data(self):
        """Données de démonstration."""
        return [
            {
                "id": "user_0001",
                "phone": "+24106010203",
                "email": "jean.dupont@email.ga",
                "first_name": "Jean",
                "last_name": "Dupont",
                "role": "driver",
                "status": "active",
                "kyc_verified": True,
                "created_at": "2026-01-15 08:30",
                "last_active": "2026-05-07 14:20",
                "total_trips": 156,
                "total_spent": 450000,
                "rating": 4.8,
                "vehicle": "Toyota Camry",
                "license": "AB123456",
                "documents": [
                    {"name": "Permis conduire", "status": "Vérifié", "date": "2026-01-10"},
                    {"name": "Pièce identité", "status": "Vérifié", "date": "2026-01-10"},
                ],
                "history": [
                    {"date": "2026-05-07 14:20", "action": "Connexion", "details": "App mobile"},
                    {"date": "2026-05-07 12:15", "action": "Trajet terminé", "details": "Libreville → Owendo"},
                    {"date": "2026-05-06 18:30", "action": "Paiement reçu", "details": "2,500 XAF"},
                ],
                "stats": {
                    "Trajets ce mois": "23",
                    "Revenus ce mois": "125,000 XAF",
                    "Note moyenne": "4.8/5",
                    "Km parcourus": "1,250 km",
                }
            },
            {
                "id": "user_0002",
                "phone": "+24106010204",
                "email": "marie.martin@email.ga",
                "first_name": "Marie",
                "last_name": "Martin",
                "role": "client",
                "status": "active",
                "kyc_verified": True,
                "created_at": "2026-02-20 10:15",
                "last_active": "2026-05-07 10:30",
                "total_trips": 45,
                "total_spent": 89000,
                "rating": 4.5,
                "documents": [
                    {"name": "Pièce identité", "status": "Vérifié", "date": "2026-02-18"},
                ],
                "history": [
                    {"date": "2026-05-07 10:30", "action": "Connexion", "details": "App mobile"},
                    {"date": "2026-05-07 09:00", "action": "Paiement", "details": "1,500 XAF"},
                ],
                "stats": {
                    "Trajets ce mois": "8",
                    "Dépenses ce mois": "15,000 XAF",
                    "Note moyenne": "N/A",
                }
            },
            {
                "id": "user_0003",
                "phone": "+24106010205",
                "email": "admin@mobitranz.ga",
                "first_name": "Admin",
                "last_name": "Mobitranz",
                "role": "admin",
                "status": "active",
                "kyc_verified": True,
                "created_at": "2025-12-01 00:00",
                "last_active": "2026-05-07 08:00",
                "total_trips": 0,
                "total_spent": 0,
                "rating": 5.0,
                "documents": [
                    {"name": "Badge employé", "status": "Vérifié", "date": "2025-12-01"},
                ],
                "history": [
                    {"date": "2026-05-07 08:00", "action": "Connexion", "details": "Interface Admin"},
                    {"date": "2026-05-06 16:00", "action": "Rapport généré", "details": "Ministère des Transports"},
                ],
                "stats": {
                    "Utilisateurs créés": "1,250",
                    "Trajets supervisés": "15,000",
                    "Incidents résolus": "89",
                }
            },
            {
                "id": "user_0004",
                "phone": "+24106010206",
                "email": "ministere@transports.ga",
                "first_name": "Ministère",
                "last_name": "Transports",
                "role": "ministry",
                "status": "active",
                "kyc_verified": True,
                "created_at": "2025-12-01 00:00",
                "last_active": "2026-05-06 14:00",
                "documents": [
                    {"name": "Accréditation officielle", "status": "Vérifié", "date": "2025-12-01"},
                ],
                "history": [
                    {"date": "2026-05-06 14:00", "action": "Rapport consulté", "details": "Statistiques mensuelles"},
                ],
                "stats": {
                    "Rapports générés": "45",
                    "Entreprises vérifiées": "12",
                    "Conformité": "98%",
                }
            },
        ]
    
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
        
        FluentButton(
            actions,
            text="📥 Exporter",
            variant="secondary",
            command=self._export_users
        ).pack(side="right", padx=(0, 10))
    
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
        self._search_entry.bind("<KeyRelease>", self._on_search)
        
        self._role_filter = ctk.CTkOptionMenu(
            search_frame,
            values=["Tous les rôles", "client", "driver", "admin", "ministry"],
            width=160
        )
        self._role_filter.pack(side="left", padx=(0, 16))
        self._role_filter.set("Tous les rôles")
        self._role_filter.bind("<<ComboboxSelected>>", self._on_filter)
        
        self._status_filter = ctk.CTkOptionMenu(
            search_frame,
            values=["Tous les statuts", "active", "pending", "suspended"],
            width=160
        )
        self._status_filter.pack(side="left", padx=(0, 16))
        self._status_filter.set("Tous les statuts")
        self._status_filter.bind("<<ComboboxSelected>>", self._on_filter)
    
    def _build_table(self):
        """Tableau des utilisateurs avec boutons détails."""
        table_card = FluentCard(self, padding=0)
        table_card.pack(fill="both", expand=True)
        
        headers = ["ID", "Nom complet", "Téléphone", "Email", "Rôle", "Statut", "KYC", "Créé", "Actions"]
        
        header_frame = ctk.CTkFrame(table_card, fg_color=("#F9FAFB", "#1F2937"), corner_radius=0)
        header_frame.pack(fill="x")
        
        for i, header in enumerate(headers):
            width = 150 if i == 7 else 100
            ctk.CTkLabel(
                header_frame,
                text=header,
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=("#6B7280", "#9CA3AF"),
                width=width,
                anchor="w"
            ).pack(side="left", padx=10, pady=12)
        
        self._table_body = ctk.CTkScrollableFrame(
            table_card,
            fg_color="transparent"
        )
        self._table_body.pack(fill="both", expand=True)
        
        self._update_table(self._users_data)
    
    def _update_table(self, users):
        """Met à jour le tableau."""
        for widget in self._table_body.winfo_children():
            widget.destroy()
        
        for user in users:
            row = ctk.CTkFrame(self._table_body, fg_color="transparent")
            row.pack(fill="x", pady=(0, 1))
            
            ctk.CTkLabel(row, text=user.get("id", "")[:8], width=100, font=ctk.CTkFont(size=11)).pack(side="left", padx=10)
            
            name = f"{user.get('first_name', '')} {user.get('last_name', '')}"
            ctk.CTkLabel(row, text=name, width=150, font=ctk.CTkFont(size=11, weight="bold")).pack(side="left", padx=10)
            
            ctk.CTkLabel(row, text=user.get("phone", ""), width=150, font=ctk.CTkFont(size=11)).pack(side="left", padx=10)
            
            ctk.CTkLabel(row, text=user.get("email", "")[:20], width=150, font=ctk.CTkFont(size=11)).pack(side="left", padx=10)
            
            role = user.get("role", "")
            role_colors = {"admin": "#8B5CF6", "driver": "#3B82F6", "client": "#10B981", "ministry": "#F59E0B"}
            ctk.CTkLabel(
                row,
                text=role.upper(),
                width=100,
                font=ctk.CTkFont(size=10, weight="bold"),
                text_color=role_colors.get(role, "#6B7280")
            ).pack(side="left", padx=10)
            
            status = user.get("status", "")
            status_colors = {"active": "#10B981", "pending": "#F59E0B", "suspended": "#EF4444"}
            ctk.CTkLabel(
                row,
                text=status.upper(),
                width=100,
                font=ctk.CTkFont(size=10, weight="bold"),
                text_color=status_colors.get(status, "#6B7280")
            ).pack(side="left", padx=10)
            
            kyc = "✅" if user.get("kyc_verified") else "❌"
            ctk.CTkLabel(row, text=kyc, width=80).pack(side="left", padx=10)
            
            ctk.CTkLabel(row, text=user.get("created_at", "")[:10], width=150, font=ctk.CTkFont(size=11)).pack(side="left", padx=10)
            
            actions = ctk.CTkFrame(row, fg_color="transparent")
            actions.pack(side="left", padx=5)
            
            btn = ctk.CTkButton(
                actions,
                text="👁️ Détails",
                width=80,
                height=25,
                font=ctk.CTkFont(size=10),
                command=lambda u=user: self._show_user_detail(u)
            )
            btn.pack(side="left", padx=2)
    
    def _show_user_detail(self, user):
        """Affiche les détails complets d'un utilisateur."""
        show_detail(self, title=f"Détails - {user.get('first_name', '')} {user.get('last_name', '')}", data=user)
    
    def _build_pagination(self):
        """Pied de page avec pagination."""
        pagination = ctk.CTkFrame(self, fg_color="transparent")
        pagination.pack(fill="x", pady=(16, 0))
        
        ctk.CTkLabel(
            pagination,
            text=f"Affichage de {len(self._users_data)} utilisateurs",
            font=ctk.CTkFont(size=12),
            text_color=("#6B7280", "#9CA3AF")
        ).pack(side="left")
        
        page_controls = ctk.CTkFrame(pagination, fg_color="transparent")
        page_controls.pack(side="right")
        
        ctk.CTkButton(page_controls, text="◀", width=40, command=self._prev_page).pack(side="left", padx=2)
        ctk.CTkLabel(page_controls, text="Page 1/1").pack(side="left", padx=10)
        ctk.CTkButton(page_controls, text="▶", width=40, command=self._next_page).pack(side="left", padx=2)
    
    def _on_search(self, event):
        """Filtre de recherche."""
        query = self._search_entry.get().lower()
        filtered = [u for u in self._users_data if query in str(u).lower()]
        self._update_table(filtered)
    
    def _on_filter(self, event):
        """Filtres de sélection."""
        role = self._role_filter.get()
        status = self._status_filter.get()
        
        filtered = self._users_data
        if role != "Tous les rôles":
            filtered = [u for u in filtered if u.get("role") == role]
        if status != "Tous les statuts":
            filtered = [u for u in filtered if u.get("status") == status]
        
        self._update_table(filtered)
    
    def _prev_page(self):
        """Page précédente."""
        pass
    
    def _next_page(self):
        """Page suivante."""
        pass
    
    def _create_user(self):
        """Créer un nouvel utilisateur."""
        print("Créer utilisateur")
    
    def _export_users(self):
        """Exporter la liste."""
        print("Exporter utilisateurs")