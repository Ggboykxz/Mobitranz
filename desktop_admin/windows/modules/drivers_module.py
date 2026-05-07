# ============================================================
# Module Drivers — Administration
# Fichier : desktop_admin/windows/modules/drivers_module.py
# ============================================================

import customtkinter as ctk
from desktop_admin.theme.components import FluentCard, KPICard, FluentButton
from desktop_admin.windows.theme.ui_theme import UITheme, get_palette, font, title_font, body_font
import random
from datetime import datetime


class DriversModule(ctk.CTkFrame):
    """Module de gestion des conducteurs."""
    
    def __init__(self, master, user_data=None, dashboard=None, **kwargs):
        kwargs.setdefault("fg_color", "transparent")
        kwargs.pop("dashboard", None)
        kwargs.pop("user_data", None)
        super().__init__(master, **kwargs)
        
        self._dashboard = dashboard
        self._current_filter = "all"
        self._sort_column = "id"
        self._sort_ascending = True
        self._filter_var = ctk.StringVar(value="all")
        self._visible_count = 15
        self._pal = get_palette()
        
        self._generate_mock_drivers()
        self._build_header()
        self._build_kpis()
        self._build_content()
    
    def _generate_mock_drivers(self):
        first_names = ["Jean", "Marie", "Pierre", "Fatou", "Ali", "Awa", "Kofi", "Amara", "Lamine", "Nadia",
                       "Youssouf", "Blessing", "Samuel", "Grace", "Ibrahim", "Esther", "Mamadou", "Aminata",
                       "Charles", "Grace", "Joseph", "Madeleine", "Thomas", "Elizabeth", "Michel", "Josiane", "David"]
        last_names = ["Ondo", "Nkog", "Manga", "Obame", "Akou", "Mba", "Essonghe", "Mouloungui", "Bongo", "Mandji",
                      "Diallo", "Konate", "Toure", "Kone", " Coulibaly", "Keita", "Traore", "Camara", "Doumbia", "Kanoute",
                      "Nguema", "Ovono", "Lefoun", "Mavial", "Ndong", "Asseko", "Moulingui"]
        cities = ["Libreville", "Port-Gentil", "Oyem", "Franceville", "Libreville", "Lambarene"]
        statuses = ["VALIDE", "VALIDE", "VALIDE", "VALIDE", "EN ATTENTE", "BLOQUE"]
        kyc_statuses = ["Valide", "Valide", "Valide", "En attente", "Expire"]
        brands = ["Toyota", "Hyundai", "Kia", "Nissan", "Honda", "Mazda", "Peugeot"]
        models = ["Corolla", "Elantra", "Sportage", "Sentra", "Civic", "3", "301"]
        
        self._drivers_data = []
        for i in range(60):
            first = random.choice(first_names)
            last = random.choice(last_names)
            phone = f"+241 0{random.randint(1,7)} {random.randint(10,99)} {random.randint(10,99)} {random.randint(10,99)}"
            status = random.choice(statuses)
            rating = f"{random.uniform(3.0, 5.0):.1f}"
            trips = random.randint(10, 800)
            earnings = random.randint(50000, 5000000)
            km = random.randint(500, 25000)
            plate_letter = chr(65 + random.randint(0, 25))
            plate_num = f"{random.randint(100, 999)}-{chr(65 + random.randint(0, 25))}{chr(65 + random.randint(0, 25))}"
            plate = f"AA-{plate_num}"
            
            self._drivers_data.append({
                "id": f"drv_{i+1:03d}",
                "phone": phone,
                "name": f"{first} {last}",
                "full_name": f"{first} {last}",
                "license": f"P-241-{random.randint(100, 999)}",
                "vehicle": plate,
                "status": status,
                "rating": rating,
                "email": f"{first.lower()}.{last.lower().replace(' ', '')}@email.ga",
                "birth_date": f"{random.randint(1,28)}/{random.randint(1,12)}/{random.randint(1975, 2000)}",
                "address": f"{random.choice(cities)}, Gabon",
                "join_date": f"{random.randint(1,25)}/0{random.randint(1,9)}/2024",
                "vehicle_brand": random.choice(brands),
                "vehicle_model": random.choice(models),
                "vehicle_year": str(random.randint(2018, 2024)),
                "trips_count": trips,
                "earnings_total": earnings,
                "km_total": km,
                "kyc_status": random.choice(kyc_statuses),
                "documents": {
                    "id": random.choice(["OK", "OK", "OK", "pending"]),
                    "permit": random.choice(["OK", "OK", "pending"]),
                    "insurance": random.choice(["OK", "OK", "expired"]),
                },
            })
    
    def _build_header(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(0, 16))
        
        title_frame = ctk.CTkFrame(header, fg_color="transparent")
        title_frame.pack(side="left")
        
        ctk.CTkLabel(title_frame, text="Gestion des conducteurs",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=("#1A3A6C", "#5B85CC")).pack(anchor="w")
        
        ctk.CTkLabel(title_frame, text=f"{len(self._drivers_data)} conducteurs enregistres",
            font=ctk.CTkFont(size=12),
            text_color=("#6B7280", "#9CA3AF")).pack(anchor="w", pady=(4, 0))
        
        right = ctk.CTkFrame(header, fg_color="transparent")
        right.pack(side="right")
        
        ctk.CTkLabel(right, text=f"🕐 {datetime.now().strftime('%H:%M:%S')}",
            font=ctk.CTkFont(size=11),
            text_color=("#9A9A9A", "#6D6D6D")).pack(side="right", padx=12)
        
        FluentButton(right, text="+ Ajouter conducteur",
            variant="primary", height=36).pack(side="right")
        
        filter_frame = ctk.CTkFrame(header, fg_color="transparent")
        filter_frame.place(relx=0.4, rely=0)
        
        filters = [
            ("Tous", "all"),
            ("Valides", "validated"),
            ("En attente", "pending"),
            ("Bloques", "blocked"),
        ]
        
        self._filter_buttons = {}
        for label, value in filters:
            btn = ctk.CTkButton(
                filter_frame,
                text=label,
                fg_color="transparent",
                hover_color=("#E5E5E5", "#3D3D3D"),
                text_color=("#5C5C5C", "#ABABAB"),
                border_width=1,
                border_color=("#E5E5E5", "#3D3D3D"),
                corner_radius=6,
                height=32,
                width=90,
                font=ctk.CTkFont(size=11),
                command=lambda f=value: self._on_filter_change(f),
            )
            btn.pack(side="left", padx=4)
            self._filter_buttons[value] = btn
        
        self._update_filter_buttons()
    
    def _update_filter_buttons(self):
        current = self._filter_var.get()
        for value, btn in self._filter_buttons.items():
            if value == current:
                btn.configure(
                    fg_color=("#1A3A6C", "#3B5EA8"),
                    text_color="white",
                    hover_color=("#142E57", "#2E5CB8"),
                )
            else:
                btn.configure(
                    fg_color="transparent",
                    text_color=("#5C5C5C", "#ABABAB"),
                    hover_color=("#E5E5E5", "#3D3D3D"),
                )
    
    def _on_filter_change(self, filter_value):
        self._filter_var.set(filter_value)
        self._current_filter = filter_value
        self._update_filter_buttons()
        self._refresh_driver_list()
    
    def _build_kpis(self):
        kpi_container = FluentCard(self, title="")
        kpi_container.pack(fill="x", pady=(0, 16))
        
        kpi_frame = ctk.CTkFrame(kpi_container, fg_color="transparent")
        kpi_frame.pack(fill="x", padx=16, pady=16)
        
        for i in range(4):
            kpi_frame.grid_columnconfigure(i, weight=1, uniform="kpi")
        
        total = len(self._drivers_data)
        validated = sum(1 for d in self._drivers_data if d["status"] == "VALIDE")
        pending = sum(1 for d in self._drivers_data if d["status"] == "EN ATTENTE")
        avg_rating = f"{sum(float(d['rating']) for d in self._drivers_data) / max(total, 1):.1f}"
        
        kpis = [
            ("🚗", "Total", str(total), "all", "#1A3A6C"),
            ("✅", "Valides", str(validated), "validated", "#009E60"),
            ("⏳", "En attente", str(pending), "pending", "#FCD116"),
            ("⭐", "Note moy.", avg_rating, "ratings", "#8B5CF6"),
        ]
        
        self._kpi_cards = []
        for i, (icon, title, value, filter_type, accent) in enumerate(kpis):
            kpi_card = self._create_clickable_kpi(kpi_frame, icon, title, value, filter_type, accent)
            kpi_card.grid(row=0, column=i, sticky="ew", padx=(0, 12 if i < 3 else 0))
            self._kpi_cards.append(kpi_card)
        
        voir_plus_btn = FluentButton(
            kpi_container,
            text="Voir plus →",
            variant="ghost",
            font=ctk.CTkFont(size=12),
            command=self._navigate_to_full_list,
        )
        voir_plus_btn.pack(anchor="e", padx=20, pady=(0, 12))
    
    def _create_clickable_kpi(self, parent, icon, title, value, filter_type, accent):
        """Crée une carte KPI cliquable."""
        card = ctk.CTkFrame(
            parent,
            fg_color=("white", "#2C2C2C"),
            border_width=1,
            border_color=("#E5E5E5", "#3D3D3D"),
            corner_radius=12,
            cursor="hand2",
        )
        
        card._filter = filter_type
        
        top_frame = ctk.CTkFrame(card, fg_color="transparent")
        top_frame.pack(fill="x", padx=20, pady=(16, 0))
        
        icon_badge = ctk.CTkLabel(
            top_frame,
            text=icon,
            font=ctk.CTkFont(size=20),
            width=40, height=40,
            fg_color=accent,
            corner_radius=10,
        )
        icon_badge.pack(side="left")
        
        ctk.CTkLabel(
            top_frame,
            text=title,
            font=ctk.CTkFont(family="Segoe UI Variable Text", size=11),
            text_color=("#6B7280", "#9CA3AF"),
            anchor="w"
        ).pack(side="left", padx=(10, 0))
        
        value_frame = ctk.CTkFrame(card, fg_color="transparent")
        value_frame.pack(fill="x", padx=20, pady=(12, 16))
        
        ctk.CTkLabel(
            value_frame,
            text=value,
            font=ctk.CTkFont(family="Segoe UI Variable Display", size=28, weight="bold"),
            text_color=("#1A1A1A", "#FFFFFF"),
            anchor="w"
        ).pack(side="left")
        
        card.bind("<Enter>", lambda e, c=card: c.configure(border_color=accent))
        card.bind("<Leave>", lambda e, c=card: c.configure(border_color=("#E5E5E5", "#3D3D3D")))
        card.bind("<Button-1>", lambda e, f=filter_type: self._on_kpi_click(f))
        
        return card
    
    def _on_kpi_click(self, filter_type):
        """Gère le clic sur une KPI."""
        if filter_type == "ratings":
            self._show_ratings_view()
        else:
            self._filter_var.set(filter_type)
            self._current_filter = filter_type
            self._update_filter_buttons()
            self._refresh_driver_list()
    
    def _show_ratings_view(self):
        """Affiche la vue des évaluations."""
        if self._dashboard:
            self._dashboard.set_module_title("Évaluations des conducteurs")
    
    def _navigate_to_full_list(self):
        """Navigate vers la liste complète des conducteurs."""
        if self._dashboard:
            self._dashboard.set_module_title("Gestion des conducteurs")
    
    def _build_content(self):
        self._list_card = FluentCard(self, title="Liste des conducteurs")
        self._list_card.pack(fill="both", expand=True)
        
        content = ctk.CTkFrame(self._list_card, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        self._content = content
        
        headers = [
            ("ID", "id"),
            ("Téléphone", "phone"),
            ("Nom", "name"),
            ("Permis", "license"),
            ("Véhicule", "vehicle"),
            ("Statut", "status"),
            ("Note", "rating"),
        ]
        
        self._header_controls = {}
        header_frame = ctk.CTkFrame(content, fg_color=("#F3F4F6", "#2D3748"))
        header_frame.pack(fill="x", pady=(0, 8))
        
        for label, col_id in headers:
            header_container = ctk.CTkFrame(header_frame, fg_color="transparent", cursor="hand2")
            header_container.pack(side="left", padx=12, pady=8)
            
            label_widget = ctk.CTkLabel(
                header_container,
                text=label,
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=("#6B7280", "#9CA3AF"),
                cursor="hand2",
            )
            label_widget.pack(side="left")
            
            sort_indicator = ctk.CTkLabel(
                header_container,
                text=" ↕",
                font=ctk.CTkFont(size=10),
                text_color=("#6B7280", "#9CA3AF"),
                cursor="hand2",
            )
            sort_indicator.pack(side="left")
            
            header_container.bind("<Button-1>", lambda e, c=col_id: self._on_sort(c))
            label_widget.bind("<Button-1>", lambda e, c=col_id: self._on_sort(c))
            sort_indicator.bind("<Button-1>", lambda e, c=col_id: self._on_sort(c))
            
            self._header_controls[col_id] = (header_container, label_widget, sort_indicator)
        
        ctk.CTkLabel(header_frame, text="Actions", font=ctk.CTkFont(size=12, weight="bold"),
                   text_color=("#6B7280", "#9CA3AF")).pack(side="left", padx=12, pady=8)
        
        self._driver_list_frame = ctk.CTkFrame(content, fg_color="transparent")
        self._driver_list_frame.pack(fill="both", expand=True)
        
        self._refresh_driver_list()
    
    def _refresh_driver_list(self):
        for widget in self._driver_list_frame.winfo_children():
            widget.destroy()
        
        filtered = self._filter_drivers()
        sorted_drivers = self._sort_drivers(filtered)
        
        for driver in sorted_drivers[:self._visible_count]:
            self._add_driver_row(driver)
        
        total = len(filtered)
        if total > self._visible_count:
            load_more = ctk.CTkButton(self._driver_list_frame, text=f"Charger plus ({total - self._visible_count} restants)",
                width=200, height=36, fg_color=("#F3F4F6", "#374151"),
                text_color=("#374151", "#E5E7EB"), hover_color=("#E5E7EB", "#4B5563"),
                font=ctk.CTkFont(size=13), command=self._load_more)
            load_more.pack(pady=16)
    
    def _load_more(self):
        self._visible_count += 15
        self._refresh_driver_list()
    
    def _filter_drivers(self):
        """Filtre les conducteurs selon le filtre courant."""
        if self._current_filter == "all":
            return self._drivers_data
        elif self._current_filter == "validated":
            return [d for d in self._drivers_data if d["status"] == "VALIDÉ"]
        elif self._current_filter == "pending":
            return [d for d in self._drivers_data if d["status"] == "EN ATTENTE"]
        elif self._current_filter == "blocked":
            return [d for d in self._drivers_data if d["status"] == "BLOQUÉ"]
        return self._drivers_data
    
    def _sort_drivers(self, drivers):
        """Trie les conducteurs selon la colonne."""
        col_map = {
            "id": "id", "phone": "phone", "name": "name",
            "license": "license", "vehicle": "vehicle",
            "status": "status", "rating": "rating",
        }
        
        key = col_map.get(self._sort_column, "id")
        reverse = not self._sort_ascending
        
        return sorted(drivers, key=lambda d: d.get(key, ""), reverse=reverse)
    
    def _on_sort(self, column):
        """Gère le tri par colonne."""
        if self._sort_column == column:
            self._sort_ascending = not self._sort_ascending
        else:
            self._sort_column = column
            self._sort_ascending = True
        
        self._update_sort_indicators()
        self._refresh_driver_list()
    
    def _update_sort_indicators(self):
        """Met à jour les indicateurs de tri."""
        for col_id, (container, label, indicator) in self._header_controls.items():
            if col_id == self._sort_column:
                arrow = " ↑" if self._sort_ascending else " ↓"
                indicator.configure(text=arrow, text_color=("#1A3A6C", "#5B85CC"))
            else:
                indicator.configure(text=" ↕", text_color=("#6B7280", "#9CA3AF"))
    
    def _add_driver_row(self, driver):
        """Ajoute une ligne de conducteur cliquable."""
        row = ctk.CTkFrame(
            self._driver_list_frame,
            fg_color=("white", "#2C2C2C"),
            corner_radius=8,
            cursor="hand2",
        )
        row.pack(fill="x", pady=2)
        
        row._driver = driver
        
        cells = [
            driver.get("id", ""),
            driver.get("phone", ""),
            driver.get("name", ""),
            driver.get("license", ""),
            driver.get("vehicle", ""),
            driver.get("status", ""),
            driver.get("rating", ""),
        ]
        
        for cell in cells:
            ctk.CTkLabel(
                row,
                text=cell,
                font=ctk.CTkFont(size=12),
                text_color=("#374151", "#D1D5DB"),
            ).pack(side="left", padx=12, pady=10)
        
        action_frame = ctk.CTkFrame(row, fg_color="transparent")
        action_frame.pack(side="left", padx=12)
        
        view_btn = ctk.CTkButton(
            action_frame,
            text="👁️",
            fg_color="transparent",
            hover_color=("#E5E5E5", "#3D3D3D"),
            width=32, height=32,
            corner_radius=6,
            command=lambda d=driver: self._show_driver_detail(d),
        )
        view_btn.pack(side="left", padx=2)
        
        row.bind("<Enter>", lambda e, r=row: r.configure(fg_color=("#F3F4F6", "#333333")))
        row.bind("<Leave>", lambda e, r=row: r.configure(fg_color=("white", "#2C2C2C")))
        row.bind("<Button-1>", lambda e, d=driver: self._show_driver_detail(d))
    
    def _show_driver_detail(self, driver):
        """Affiche le drawer des détails du conducteur."""
        detail_drawer = DriverDetailDrawer(self, driver)
        detail_drawer.show()


class DriverDetailDrawer(ctk.CTkToplevel):
    """Drawer de détails pour un conducteur."""
    
    def __init__(self, master, driver):
        super().__init__(master)
        
        self._driver = driver
        self._setup_window()
        self._build_content()
    
    def _setup_window(self):
        """Configure la fenêtre drawer."""
        width = 600
        height = 700
        
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        
        x = screen_width - width - 50
        y = (screen_height - height) // 2
        
        self.geometry(f"{width}x{height}+{x}+{y}")
        self.resizable(False, False)
        self.attributes("-topmost", True)
        
        self.configure(fg_color=("#F5F5F5", "#1A1A1A"))
        
        self.transient(self.master)
        self.grab_set()
    
    def _build_content(self):
        """Construit le contenu du drawer."""
        main_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True)
        
        header = ctk.CTkFrame(main_frame, fg_color=("#1A3A6C", "#2E5CB8"))
        header.pack(fill="x", pady=(0, 16))
        
        ctk.CTkLabel(
            header,
            text=f"👤 {self._driver.get('full_name', self._driver.get('name'))}",
            font=ctk.CTkFont(family="Segoe UI Variable Display", size=18, weight="bold"),
            text_color="white",
        ).pack(padx=20, pady=16)
        
        close_btn = ctk.CTkButton(
            header,
            text="✕",
            fg_color="transparent",
            hover_color=("#142E57", "#1E3E78"),
            width=36, height=36,
            corner_radius=18,
            command=self.destroy,
        )
        close_btn.pack(padx=16, pady=16, side="right")
        
        self._build_profile_section(main_frame)
        self._build_vehicle_section(main_frame)
        self._build_trips_section(main_frame)
        self._build_earnings_section(main_frame)
        self._build_kyc_section(main_frame)
        self._build_ratings_section(main_frame)
    
    def _build_section(self, parent, title):
        """Crée une section avec titre."""
        card = FluentCard(parent, title=title, padding=16)
        card.pack(fill="x", pady=(0, 12))
        
        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(fill="x", padx=8, pady=(0, 8))
        
        return content
    
    def _build_profile_section(self, parent):
        """Section profil."""
        content = self._build_section(parent, "👤 Profil du conducteur")
        
        info = [
            ("ID", self._driver.get("id")),
            ("Téléphone", self._driver.get("phone")),
            ("Email", self._driver.get("email")),
            ("Date de naissance", self._driver.get("birth_date")),
            ("Adresse", self._driver.get("address")),
            ("Date d'inscription", self._driver.get("join_date")),
            ("Statut", self._driver.get("status")),
        ]
        
        for label, value in info:
            row = ctk.CTkFrame(content, fg_color="transparent")
            row.pack(fill="x", pady=4)
            
            ctk.CTkLabel(
                row,
                text=label,
                font=ctk.CTkFont(size=12),
                text_color=("#6B7280", "#9CA3AF"),
                width=120,
                anchor="w",
            ).pack(side="left")
            
            ctk.CTkLabel(
                row,
                text=str(value) if value else "-",
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=("#1A1A1A", "#FFFFFF"),
                anchor="w",
            ).pack(side="left")
    
    def _build_vehicle_section(self, parent):
        """Section véhicule."""
        content = self._build_section(parent, "🚗 Véhicule")
        
        info = [
            ("Immatriculation", self._driver.get("vehicle")),
            ("Marque", self._driver.get("vehicle_brand")),
            ("Modèle", self._driver.get("vehicle_model")),
            ("Année", str(self._driver.get("vehicle_year", "-"))),
        ]
        
        for label, value in info:
            row = ctk.CTkFrame(content, fg_color="transparent")
            row.pack(fill="x", pady=4)
            
            ctk.CTkLabel(
                row,
                text=label,
                font=ctk.CTkFont(size=12),
                text_color=("#6B7280", "#9CA3AF"),
                width=120,
                anchor="w",
            ).pack(side="left")
            
            ctk.CTkLabel(
                row,
                text=str(value) if value else "-",
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=("#1A1A1A", "#FFFFFF"),
                anchor="w",
            ).pack(side="left")
    
    def _build_trips_section(self, parent):
        """Section historique des trajets."""
        content = self._build_section(parent, "🗺️ Historique des trajets")
        
        trips = [
            {"date": "25/04/2026", "from": "Libreville Centre", "to": "Aéroport", "fare": "5000", "status": "Terminé"},
            {"date": "24/04/2026", "from": "Port-Gentil", "to": "Libreville", "fare": "15000", "status": "Terminé"},
            {"date": "23/04/2026", "from": "Okala", "to": "Nkou", "fare": "3500", "status": "Annulé"},
        ]
        
        for trip in trips:
            trip_row = ctk.CTkFrame(content, fg_color=("#F3F4F6", "#2D3748"), corner_radius=6)
            trip_row.pack(fill="x", pady=4)
            
            ctk.CTkLabel(
                trip_row,
                text=trip["date"],
                font=ctk.CTkFont(size=11),
                text_color=("#6B7280", "#9CA3AF"),
                width=70,
            ).pack(side="left", padx=8, pady=8)
            
            ctk.CTkLabel(
                trip_row,
                text=f"{trip['from']} → {trip['to']}",
                font=ctk.CTkFont(size=11),
                text_color=("#1A1A1A", "#FFFFFF"),
            ).pack(side="left", padx=8)
            
            ctk.CTkLabel(
                trip_row,
                text=f"{trip['fare']} XAF",
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color=("#009E60", "#4DC882"),
            ).pack(side="left", padx=8)
            
            status_colors = {"Terminé": "#009E60", "Annulé": "#E53E3E"}
            status_color = status_colors.get(trip["status"], "#6B7280")
            ctk.CTkLabel(
                trip_row,
                text=trip["status"],
                font=ctk.CTkFont(size=10),
                text_color=status_color,
            ).pack(side="right", padx=8)
    
    def _build_earnings_section(self, parent):
        """Section revenus."""
        content = self._build_section(parent, "💰 Statistiques de revenus")
        
        info = [
            ("Total des revenus", f"{self._driver.get('earnings_total', 0):,} XAF"),
            ("Nombre de courses", str(self._driver.get('trips_count', 0))),
            ("Kilomètres parcourus", f"{self._driver.get('km_total', 0):,} km"),
            ("Revenu moyen/course", f"{self._driver.get('earnings_total', 0) // max(self._driver.get('trips_count', 1), 1):,} XAF"),
        ]
        
        for label, value in info:
            row = ctk.CTkFrame(content, fg_color="transparent")
            row.pack(fill="x", pady=4)
            
            ctk.CTkLabel(
                row,
                text=label,
                font=ctk.CTkFont(size=12),
                text_color=("#6B7280", "#9CA3AF"),
                width=180,
                anchor="w",
            ).pack(side="left")
            
            ctk.CTkLabel(
                row,
                text=str(value),
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=("#009E60", "#4DC882"),
                anchor="w",
            ).pack(side="left")
    
    def _build_kyc_section(self, parent):
        """Section documents KYC."""
        content = self._build_section(parent, "📄 Documents KYC")
        
        status = self._driver.get("kyc_status", "Inconnu")
        status_colors = {"Validé": "#009E60", "En attente": "#FCD116", "Expiré": "#E53E3E"}
        status_color = status_colors.get(status, "#6B7280")
        
        ctk.CTkLabel(
            content,
            text=f"Statut: {status}",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=status_color,
        ).pack(anchor="w", pady=(0, 12))
        
        docs = self._driver.get("documents", {})
        for doc_name, doc_status in docs.items():
            row = ctk.CTkFrame(content, fg_color="transparent")
            row.pack(fill="x", pady=4)
            
            names = {"id": "Pièce d'identité", "permit": "Permis de conduire", "insurance": "Assurance"}
            ctk.CTkLabel(
                row,
                text=names.get(doc_name, doc_name),
                font=ctk.CTkFont(size=12),
                text_color=("#1A1A1A", "#FFFFFF"),
                width=150,
                anchor="w",
            ).pack(side="left")
            
            status_symbol = "✓" if doc_status == "✓" else doc_status
            symbol_color = "#009E60" if doc_status == "✓" else "#E53E3E" if doc_status == "✗" else "#FCD116"
            ctk.CTkLabel(
                row,
                text=status_symbol,
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color=symbol_color,
            ).pack(side="left")
    
    def _build_ratings_section(self, parent):
        """Section évaluations."""
        content = self._build_section(parent, "⭐ Évaluations")
        
        current_rating = self._driver.get("rating", "N/A")
        
        rating_frame = ctk.CTkFrame(content, fg_color="transparent")
        rating_frame.pack(fill="x", pady=(0, 12))
        
        ctk.CTkLabel(
            rating_frame,
            text=f"Note actuelle: {current_rating}/5.0",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=("#FCD116", "#E6BC00"),
        ).pack(side="left")
        
        ratings = [
            {"date": "Avril 2026", "rating": "4.8", "trips": 45},
            {"date": "Mars 2026", "rating": "4.7", "trips": 52},
            {"date": "Février 2026", "rating": "4.9", "trips": 48},
            {"date": "Janvier 2026", "rating": "4.6", "trips": 50},
        ]
        
        ctk.CTkLabel(
            content,
            text="Historique:",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=("#1A1A1A", "#FFFFFF"),
        ).pack(anchor="w", pady=(8, 4))
        
        for r in ratings:
            row = ctk.CTkFrame(content, fg_color="transparent")
            row.pack(fill="x", pady=2)
            
            ctk.CTkLabel(
                row,
                text=r["date"],
                font=ctk.CTkFont(size=11),
                text_color=("#6B7280", "#9CA3AF"),
                width=100,
            ).pack(side="left")
            
            stars = "⭐" * int(float(r["rating"]))
            ctk.CTkLabel(
                row,
                text=f"{stars} {r['rating']}",
                font=ctk.CTkFont(size=11),
                text_color=("#FCD116", "#E6BC00"),
            ).pack(side="left")
            
            ctk.CTkLabel(
                row,
                text=f"({r['trips']} courses)",
                font=ctk.CTkFont(size=10),
                text_color=("#9A9A9A", "#6D6D6D"),
            ).pack(side="right")


if __name__ == "__main__":
    app = ctk.CTk()
    app.geometry("1200x800")
    module = DriversModule(app)
    module.pack(fill="both", expand=True, padx=20, pady=20)
    app.mainloop()