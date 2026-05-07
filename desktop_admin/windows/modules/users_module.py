# ============================================================
# Module Users — Administration
# Fichier : desktop_admin/windows/modules/users_module.py
# Description : CRUD utilisateurs, KYC, suspension
# ============================================================

import customtkinter as ctk
from desktop_admin.theme.components import FluentCard, FluentButton
from desktop_admin.windows.theme.ui_theme import UITheme, get_palette, font, title_font, body_font
import random
from datetime import datetime


class UsersModule(ctk.CTkFrame):
    """Module de gestion des utilisateurs."""
    
    TOTAL_KPI = "total"
    ACTIVE_KPI = "active"
    DRIVER_KPI = "driver"
    PENDING_KPI = "pending"
    
    def __init__(self, master, user_data=None, dashboard=None, **kwargs):
        kwargs.setdefault("fg_color", "transparent")
        kwargs.pop("dashboard", None)
        kwargs.pop("user_data", None)
        super().__init__(master, **kwargs)
        
        self._user_data = user_data or {}
        self._current_filter = None
        self._search_text = ""
        self._role_filter = "TOUS"
        self._status_filter = "TOUS"
        self._visible_count = 10
        self._total_shown = 10
        self._pal = get_palette()
        
        self._generate_mock_users()
        self._build_header()
        self._build_kpis()
        self._build_filters()
        self._build_user_list()
        self._build_load_more()
        
        self._drawer = None
    
    def _get_colors(self):
        return get_palette()
    
    def _generate_mock_users(self):
        first_names = ["Jean", "Marie", "Pierre", "Fatou", "Ali", "Awa", "Kofi", "Amara", "Lamine", "Nadia",
                       "Youssouf", "Blessing", "Samuel", "Grace", "Ibrahim", "Esther", "Mamadou", "Aminata",
                       "Charles", "Charlotte", "Joseph", "Madeleine", "Thomas", "Elizabeth", "Michel", "Josiane"]
        last_names = ["Ondo", "Nkog", "Manga", "Obame", "Akou", "Mba", "Essonghe", "Mouloungui", "Bongo", "Mandji",
                      "Diallo", "Konate", "Toure", "Kone", " Coulibaly", "Keita", "Traore", "Camara", "Doumbia", "Kanoute",
                      "Nguema", "Ovono", "Lefoun", "Mavial", "Ndong", "Asseko"]
        domains = ["orange.ga", "airtel.ga", "moov.ga", "gabon telecom.ga"]
        
        self._all_users = []
        for i in range(100):
            first = random.choice(first_names)
            last = random.choice(last_names)
            phone = f"+241 0{random.randint(1,7)} {random.randint(10,99)} {random.randint(10,99)} {random.randint(10,99)}"
            email = f"{first.lower()}.{last.lower().replace(' ', '')}{i}@{random.choice(domains)}"
            role = random.choice(["CLIENT", "CLIENT", "CLIENT", "DRIVER", "ADMIN"])
            statuses = ["ACTIF", "ACTIF", "ACTIF", "ACTIF", "SUSPENDU", "EN_ATTENTE"]
            status = random.choice(statuses)
            kyc_statuses = ["VERIFIE", "VERIFIE", "VERIFIE", "EN_ATTENTE", "REJETE"]
            kyc = random.choice(kyc_statuses)
            created = f"{random.randint(1,25)}/04/2026 {random.randint(0,23):02d}:{random.randint(0,59):02d}"
            trips = random.randint(0, 150)
            rating = f"{random.uniform(3.5, 5.0):.1f}"
            balance = f"{random.randint(0, 500000):,}"
            
            self._all_users.append({
                "id": f"usr_{i+1:03d}",
                "first": first,
                "last": last,
                "name": f"{first} {last}",
                "phone": phone,
                "email": email,
                "role": role,
                "status": status,
                "kyc": kyc,
                "created": created,
                "trips": trips,
                "rating": rating,
                "balance": balance,
                "avatar": f"{first[0]}{last[0]}",
            })
    
    def _build_header(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(0, 16))
        
        title_frame = ctk.CTkFrame(header, fg_color="transparent")
        title_frame.pack(side="left")
        
        ctk.CTkLabel(title_frame, text="Gestion des utilisateurs",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=("#1A3A6C", "#5B85CC")).pack(anchor="w")
        
        ctk.CTkLabel(title_frame, text=f"{len(self._all_users)} utilisateurs inscrits — Gabon",
            font=ctk.CTkFont(size=12),
            text_color=("#6B7280", "#9CA3AF")).pack(anchor="w", pady=(4, 0))
        
        right = ctk.CTkFrame(header, fg_color="transparent")
        right.pack(side="right")
        
        ctk.CTkLabel(right, text=f"🕐 {datetime.now().strftime('%H:%M:%S')}",
            font=ctk.CTkFont(size=11),
            text_color=("#9A9A9A", "#6D6D6D")).pack(side="right", padx=12)
        
        FluentButton(right, text="+ Ajouter utilisateur",
            variant="primary", height=36).pack(side="right")
    
    def _build_kpis(self):
        kpi_frame = ctk.CTkFrame(self, fg_color="transparent")
        kpi_frame.pack(fill="x", pady=(0, 16))
        for i in range(4):
            kpi_frame.grid_columnconfigure(i, weight=1)
        
        total = len(self._all_users)
        active = sum(1 for u in self._all_users if u["status"] == "ACTIF")
        drivers = sum(1 for u in self._all_users if u["role"] == "DRIVER")
        pending = sum(1 for u in self._all_users if u["kyc"] in ("EN_ATTENTE", "REJETE"))
        
        kpis_data = [
            (self.TOTAL_KPI, "Total utilisateurs", str(total), "#6366F1"),
            (self.ACTIVE_KPI, "Utilisateurs actifs", str(active), "#10B981"),
            (self.DRIVER_KPI, "Chauffeurs", str(drivers), "#F59E0B"),
            (self.PENDING_KPI, "En attente KYC", str(pending), "#EF4444"),
        ]
        
        self._kpis = {}
        for kpi_id, label, value, color in kpis_data:
            card = ctk.CTkFrame(kpi_frame, fg_color=("white", "#1F2937"), corner_radius=12)
            card.pack(side="left", padx=(0, 12), fill="both", expand=True)
            card.bind("<Button-1>", lambda e, k=kpi_id: self._on_kpi_click(k))
            card.configure(cursor="hand2")
            
            ctk.CTkLabel(card, text=label, font=ctk.CTkFont(size=12),
                text_color=("#6B7280", "#9CA3AF")).pack(anchor="w", padx=16, pady=(16, 4))
            
            ctk.CTkLabel(card, text=value, font=ctk.CTkFont(size=28, weight="bold"),
                text_color=(color, color)).pack(anchor="w", padx=16, pady=(0, 16))
            
            self._kpis[kpi_id] = {"card": card, "value": value, "label": label}
    
    def _build_filters(self):
        filter_card = FluentCard(self, title="")
        filter_card.pack(fill="x", pady=(0, 16))
        
        filter_content = ctk.CTkFrame(filter_card, fg_color="transparent")
        filter_content.pack(fill="x", padx=16, pady=12)
        
        search = ctk.CTkEntry(filter_content, placeholder_text="Rechercher par nom, telephone ou email...",
            width=320, height=36)
        search.pack(side="left", padx=(0, 12))
        search.bind("<KeyRelease>", self._on_search)
        self._search_entry = search
        
        roles = ["TOUS", "CLIENT", "DRIVER", "ADMIN"]
        role_menu = ctk.CTkOptionMenu(filter_content, values=roles, width=140, height=36,
            command=lambda v: self._on_filter_change("role", v))
        role_menu.pack(side="left", padx=(0, 12))
        
        statuses = ["TOUS", "ACTIF", "SUSPENDU", "EN_ATTENTE"]
        status_menu = ctk.CTkOptionMenu(filter_content, values=statuses, width=140, height=36,
            command=lambda v: self._on_filter_change("status", v))
        status_menu.pack(side="left", padx=(0, 12))
        
        export_btn = ctk.CTkButton(filter_content, text="Exporter CSV",
            width=120, height=36, fg_color=("#10B981", "#059669"),
            hover_color=("#059669", "#047857"))
        export_btn.pack(side="right")
        
        self._role_menu = role_menu
        self._status_menu = status_menu
    
    def _on_filter_change(self, ftype, value):
        if ftype == "role":
            self._role_filter = value
        else:
            self._status_filter = value
        self._refresh_list()
    
    def _on_search(self, event):
        self._search_text = event.widget.get()
        self._refresh_list()
    
    def _on_kpi_click(self, kpi_id):
        self._current_filter = kpi_id if self._current_filter != kpi_id else None
        for kid, kdata in self._kpis.items():
            if kid == self._current_filter:
                kdata["card"].configure(border_color=("#6366F1", "#6366F1"), border_width=2)
            else:
                kdata["card"].configure(border_color="transparent", border_width=0)
        self._refresh_list()
    
    def _build_user_list(self):
        list_card = FluentCard(self, title="")
        list_card.pack(fill="both", expand=True, pady=(0, 16))
        
        self._list_container = ctk.CTkFrame(list_card, fg_color="transparent")
        self._list_container.pack(fill="both", expand=True, padx=16, pady=16)
        
        self._user_rows = []
        self._render_users()
    
    def _render_users(self):
        for widget in self._list_container.winfo_children():
            widget.destroy()
        
        header_frame = ctk.CTkFrame(self._list_container, fg_color=("#F3F4F6", "#2D3748"))
        header_frame.pack(fill="x", pady=(0, 8))
        
        headers = ["Utilisateur", "Telephone", "Email", "Role", "Statut", "KYC", "Trajets", "Actions"]
        widths = [160, 140, 180, 80, 80, 80, 60, 100]
        
        for h, w in zip(headers, widths):
            ctk.CTkLabel(header_frame, text=h, font=ctk.CTkFont(size=11, weight="bold"),
                text_color=("#6B7280", "#9CA3AF"), width=w).pack(side="left", padx=8, pady=8)
        
        users = self._get_filtered_users()
        self._user_rows = []
        
        for user in users[:self._visible_count]:
            self._create_user_row(user)
    
    def _create_user_row(self, user):
        row = ctk.CTkFrame(self._list_container, fg_color=("white", "#2C2C2C"), corner_radius=8)
        row.pack(fill="x", pady=2)
        row.bind("<Button-1>", lambda e, u=user: self._show_user_drawer(u))
        row.configure(cursor="hand2")
        
        avatar_colors = ["#1A3A6C", "#009E60", "#6366F1", "#F59E0B", "#EF4444", "#8B5CF6"]
        avatar_color = avatar_colors[hash(user["name"]) % len(avatar_colors)]
        
        avatar_frame = ctk.CTkFrame(row, fg_color=avatar_color, width=36, height=36, corner_radius=18)
        avatar_frame.pack(side="left", padx=(12, 4))
        avatar_frame.pack_propagate(False)
        ctk.CTkLabel(avatar_frame, text=user["avatar"],
            font=ctk.CTkFont(size=12, weight="bold"), text_color="white").pack(expand=True)
        
        name_frame = ctk.CTkFrame(row, fg_color="transparent")
        name_frame.pack(side="left", padx=(0, 8))
        name_frame.bind("<Button-1>", lambda e, u=user: self._show_user_drawer(u))
        
        ctk.CTkLabel(name_frame, text=user["name"], font=ctk.CTkFont(size=12, weight="bold"),
            text_color=("#1F2937", "#F9FAFB")).pack(anchor="w")
        ctk.CTkLabel(name_frame, text=user["id"], font=ctk.CTkFont(size=10),
            text_color=("#9CA3AF", "#6B7280")).pack(anchor="w")
        
        phone = ctk.CTkLabel(row, text=user["phone"], font=ctk.CTkFont(size=11),
            text_color=("#374151", "#D1D5DB"), width=140)
        phone.pack(side="left", padx=8)
        phone.bind("<Button-1>", lambda e, u=user: self._show_user_drawer(u))
        phone.configure(cursor="hand2")
        
        email = ctk.CTkLabel(row, text=user["email"], font=ctk.CTkFont(size=11),
            text_color=("#374151", "#D1D5DB"), width=180)
        email.pack(side="left", padx=8)
        email.bind("<Button-1>", lambda e, u=user: self._show_user_drawer(u))
        email.configure(cursor="hand2")
        
        role_colors = {"CLIENT": ("#EEF2FF", "#6366F1"), "DRIVER": ("#ECFDF5", "#10B981"), "ADMIN": ("#FEF3C7", "#F59E0B")}
        bg, fg = role_colors.get(user["role"], ("#F3F4F6", "#6B7280"))
        role_lbl = ctk.CTkLabel(row, text=user["role"], font=ctk.CTkFont(size=10, weight="bold"),
            text_color=fg, width=80)
        role_lbl.pack(side="left", padx=8)
        
        status_colors = {"ACTIF": "#10B981", "SUSPENDU": "#EF4444", "EN_ATTENTE": "#F59E0B"}
        status_lbl = ctk.CTkLabel(row, text=user["status"], font=ctk.CTkFont(size=10, weight="bold"),
            text_color=(status_colors.get(user["status"], "#6B7280"), status_colors.get(user["status"], "#9CA3AF")), width=80)
        status_lbl.pack(side="left", padx=8)
        
        kyc_colors = {"VERIFIE": "#10B981", "EN_ATTENTE": "#F59E0B", "REJETE": "#EF4444"}
        kyc_lbl = ctk.CTkLabel(row, text=user["kyc"], font=ctk.CTkFont(size=10),
            text_color=(kyc_colors.get(user["kyc"], "#6B7280"), kyc_colors.get(user["kyc"], "#9CA3AF")), width=80)
        kyc_lbl.pack(side="left", padx=8)
        
        trips_lbl = ctk.CTkLabel(row, text=str(user["trips"]), font=ctk.CTkFont(size=11),
            text_color=("#374151", "#D1D5DB"), width=60)
        trips_lbl.pack(side="left", padx=8)
        
        actions_frame = ctk.CTkFrame(row, fg_color="transparent", width=100)
        actions_frame.pack(side="left", padx=8)
        
        btn_view = ctk.CTkButton(actions_frame, text="Voir", width=50, height=28,
            fg_color=("#EEF2FF", "#312E81"), text_color=("#6366F1", "#A5B4FC"),
            hover_color=("#C7D2FE", "#4338CA"), font=ctk.CTkFont(size=11),
            command=lambda u=user: self._show_user_drawer(u))
        btn_view.pack(side="left", padx=2)
        
        btn_menu = ctk.CTkButton(actions_frame, text="...", width=30, height=28,
            fg_color=("#F3F4F6", "#374151"), text_color=("#6B7280", "#9CA3AF"),
            hover_color=("#E5E7EB", "#4B5563"), font=ctk.CTkFont(size=11),
            command=lambda u=user: self._show_user_menu(u))
        btn_menu.pack(side="left", padx=2)
        
        self._user_rows.append(row)
    
    def _get_filtered_users(self):
        filtered = list(self._all_users)
        
        if self._current_filter == self.TOTAL_KPI:
            pass
        elif self._current_filter == self.ACTIVE_KPI:
            filtered = [u for u in filtered if u["status"] == "ACTIF"]
        elif self._current_filter == self.DRIVER_KPI:
            filtered = [u for u in filtered if u["role"] == "DRIVER"]
        elif self._current_filter == self.PENDING_KPI:
            filtered = [u for u in filtered if u["kyc"] in ("EN_ATTENTE", "REJETE")]
        
        if self._role_filter != "TOUS":
            filtered = [u for u in filtered if u["role"] == self._role_filter]
        
        if self._status_filter != "TOUS":
            filtered = [u for u in filtered if u["status"] == self._status_filter]
        
        if self._search_text:
            search = self._search_text.lower()
            filtered = [u for u in filtered if search in u["name"].lower() or search in u["phone"] or search in u["email"]]
        
        self._total_shown = len(filtered)
        return filtered
    
    def _refresh_list(self):
        self._visible_count = self._total_shown
        self._render_users()
    
    def _build_load_more(self):
        self._load_more_btn = ctk.CTkButton(self, text="Voir plus",
            width=200, height=40, fg_color=("#F3F4F6", "#374151"),
            text_color=("#374151", "#E5E7EB"), hover_color=("#E5E7EB", "#4B5563"),
            font=ctk.CTkFont(size=14, weight="bold"),
            command=lambda: setattr(self, "_visible_count", min(self._visible_count + 10, self._total_shown)) or self._refresh_list())
        self._load_more_btn.pack(pady=(0, 16))
    
    def _show_user_drawer(self, user):
        if self._drawer and self._drawer.winfo_exists():
            self._drawer.destroy()
        
        self._drawer = ctk.CTkToplevel(self)
        self._drawer.title(f"Profil — {user['name']}")
        self._drawer.geometry("540x780")
        self._drawer.resizable(False, False)
        self._drawer.transient(self.winfo_toplevel())
        self._drawer.grab_set()
        
        drawer_bg = ctk.CTkFrame(self._drawer, fg_color=("white", "#111827"))
        drawer_bg.pack(fill="both", expand=True)
        
        header = ctk.CTkFrame(drawer_bg, fg_color=("#F8FAFC", "#0F172A"))
        header.pack(fill="x", pady=(0, 20))
        
        avatar_colors = ["#1A3A6C", "#009E60", "#6366F1", "#F59E0B", "#EF4444", "#8B5CF6"]
        avatar_color = avatar_colors[hash(user["name"]) % len(avatar_colors)]
        avatar_frame = ctk.CTkFrame(header, fg_color=avatar_color, width=72, height=72, corner_radius=36)
        avatar_frame.pack(pady=20)
        avatar_frame.pack_propagate(False)
        ctk.CTkLabel(avatar_frame, text=user["avatar"],
            font=ctk.CTkFont(size=28, weight="bold"), text_color="white").pack(expand=True)
        
        ctk.CTkLabel(header, text=user["name"],
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=("#1F2937", "#F9FAFB")).pack()
        
        role_colors = {"CLIENT": "#6366F1", "DRIVER": "#10B981", "ADMIN": "#F59E0B"}
        ctk.CTkLabel(header, text=f"{user['role']} • {user['status']}",
            font=ctk.CTkFont(size=13),
            text_color=(role_colors.get(user["role"], "#6B7280"), "#9CA3AF")).pack(pady=(4, 0))
        
        close_btn = ctk.CTkButton(header, text="✕", width=36, height=36,
            fg_color="transparent", text_color=("#6B7280", "#9CA3AF"),
            hover_color=("#E5E7EB", "#374151"))
        close_btn.place(relx=0.95, rely=0.05, anchor="ne")
        close_btn.bind("<Button-1>", lambda e: self._drawer.destroy())
        close_btn.configure(cursor="hand2")
        
        content = ctk.CTkScrollableFrame(drawer_bg, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=20)
        
        stats_row = ctk.CTkFrame(content, fg_color="transparent")
        stats_row.pack(fill="x", pady=(0, 16))
        for i in range(3):
            stats_row.grid_columnconfigure(i, weight=1)
        
        stats = [
            ("🛣️", f"{user['trips']}", "Trajets"),
            ("⭐", user["rating"], "Note"),
            ("💰", f"{user['balance']}", "Solde XAF"),
        ]
        for i, (icon, val, label) in enumerate(stats):
            stat_card = ctk.CTkFrame(stats_row, fg_color=("white", "#1F2937"), corner_radius=10)
            stat_card.grid(row=0, column=i, padx=4)
            ctk.CTkLabel(stat_card, text=icon, font=ctk.CTkFont(size=20)).pack(pady=(12, 4))
            ctk.CTkLabel(stat_card, text=str(val), font=ctk.CTkFont(size=16, weight="bold"),
                text_color=("#1A3A6C", "#5B85CC")).pack()
            ctk.CTkLabel(stat_card, text=label, font=ctk.CTkFont(size=11),
                text_color=("#6B7280", "#9CA3AF")).pack(pady=(0, 12))
        
        self._drawer_section(content, "Coordonnees", [
            ("ID", user["id"]),
            ("Telephone", user["phone"]),
            ("Email", user["email"]),
            ("Inscrit le", user["created"]),
        ])
        
        kyc_section = self._drawer_section(content, "Verification KYC", [])
        kyc_colors = {"VERIFIE": "#10B981", "EN_ATTENTE": "#F59E0B", "REJETE": "#EF4444"}
        kyc_bg_colors = {"VERIFIE": ("#ECFDF5", "#065F46"), "EN_ATTENTE": ("#FFFBEB", "#92400E"), "REJETE": ("#FEF2F2", "#991B1B")}
        bg_c, fg_c = kyc_bg_colors.get(user["kyc"], ("#F3F4F6", "#6B7280"))
        kyc_badge = ctk.CTkFrame(kyc_section, fg_color=bg_c, corner_radius=8)
        kyc_badge.pack(anchor="w", padx=16, pady=8)
        ctk.CTkLabel(kyc_badge, text=user["kyc"], font=ctk.CTkFont(size=13, weight="bold"),
            text_color=fg_c).pack(padx=12, pady=8)
        
        actions_row = ctk.CTkFrame(content, fg_color="transparent")
        actions_row.pack(fill="x", pady=(0, 16))
        
        FluentButton(actions_row, text="Modifier le role", variant="secondary", height=40).pack(side="left", padx=(0, 8), fill="x", expand=True)
        FluentButton(actions_row, text="Suspendre", variant="warning", height=40).pack(side="left", padx=(0, 8), fill="x", expand=True)
        FluentButton(actions_row, text="Supprimer", variant="danger", height=40).pack(side="left", fill="x", expand=True)
    
    def _drawer_section(self, parent, title, fields):
        section = ctk.CTkFrame(parent, fg_color=("white", "#1F2937"), corner_radius=12)
        section.pack(fill="x", pady=(0, 12))
        ctk.CTkLabel(section, text=title, font=ctk.CTkFont(size=14, weight="bold"),
            text_color=("#1F2937", "#F9FAFB")).pack(anchor="w", padx=16, pady=(12, 8))
        for label, value in fields:
            field = ctk.CTkFrame(section, fg_color="transparent")
            field.pack(fill="x", padx=16, pady=2)
            ctk.CTkLabel(field, text=f"{label}:", font=ctk.CTkFont(size=12),
                text_color=("#6B7280", "#9CA3AF"), width=100, anchor="w").pack(side="left")
            ctk.CTkLabel(field, text=value, font=ctk.CTkFont(size=12),
                text_color=("#1F2937", "#F9FAFB")).pack(side="left")
        return section
    
    def _show_user_menu(self, user):
        print(f"Menu for {user['name']}")