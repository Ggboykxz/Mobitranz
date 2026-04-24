# ============================================================
# Module Vue d'ensemble — Dashboard principal
# Fichier : desktop_admin/windows/modules/overview_module.py
# Description : KPIs temps réel, graphiques, activité récente
# ============================================================

import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from desktop_admin.theme.components import KPICard, FluentCard, FluentButton


class OverviewModule(ctk.CTkFrame):
    """Module tableau de bord principal — Vue d'ensemble MobiTranz.
    
    Sections :
    1. KPIs en temps réel (4 cartes en ligne)
    2. Graphique trajets de la semaine (matplotlib)
    3. Carte activité + Tableau activité récente
    """
    
    def __init__(self, master, user_data=None, **kwargs):
        kwargs.setdefault("fg_color", "transparent")
        super().__init__(master, **kwargs)
        
        self._user_data = user_data or {}
        self._refresh_interval = 30000
        
        self._build_header()
        self._build_kpi_row()
        self._build_charts_row()
        self._build_recent_activity()
        
        self._schedule_refresh()
    
    def _build_header(self):
        """En-tête avec date et bouton refresh."""
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(0, 16))
        header.grid_columnconfigure(1, weight=1)
        
        from datetime import datetime
        hour = datetime.now().hour
        greeting = "Bonjour" if 5 <= hour < 12 else "Bon après-midi" if 12 <= hour < 18 else "Bonsoir"
        email = self._user_data.get("email", "Admin")
        
        ctk.CTkLabel(
            header,
            text=f"{greeting}, {email.split('@')[0].capitalize()} 👋",
            font=ctk.CTkFont(family="Segoe UI Variable Display", size=22, weight="bold"),
            text_color=("#1A1A1A", "white"),
            anchor="w"
        ).pack(side="left")
        
        right_frame = ctk.CTkFrame(header, fg_color="transparent")
        right_frame.pack(side="right")
        
        self._last_update_label = ctk.CTkLabel(
            right_frame,
            text=f"Mis à jour : {datetime.now().strftime('%H:%M:%S')}",
            font=ctk.CTkFont(size=12),
            text_color=("#9A9A9A", "#6D6D6D"),
        )
        self._last_update_label.pack(side="left", padx=(0, 12))
        
        FluentButton(
            right_frame, text="↻  Actualiser",
            variant="secondary", height=36,
            command=self._refresh_data
        ).pack(side="left")
    
    def _build_kpi_row(self):
        """Grille 4 KPIs."""
        kpi_frame = ctk.CTkFrame(self, fg_color="transparent")
        kpi_frame.pack(fill="x", pady=(0, 16))
        
        for i in range(4):
            kpi_frame.grid_columnconfigure(i, weight=1, uniform="kpi")
        
        kpis = [
            ("🚗", "Trajets actifs",    "127",      "+12",  "#1A3A6C", 12),
            ("💰", "Revenus du jour",   "2,840,500","XAF",  "#009E60", 8),
            ("👥", "Utilisateurs",      "15,234",   "+47",  "#FCD116", 47),
            ("🚨", "Incidents ouverts", "3",        None,   "#E53E3E", None),
        ]
        
        for i, (icon, title, value, trend_or_unit, color, trend_val) in enumerate(kpis):
            card = KPICard(
                kpi_frame,
                icon=icon, title=title, value=value,
                unit=trend_or_unit if trend_val is None and not isinstance(trend_or_unit, int) else "",
                trend=trend_val,
                accent_color=color,
            )
            card.grid(row=0, column=i, sticky="ew", padx=(0, 12 if i < 3 else 0))
    
    def _build_charts_row(self):
        """Ligne graphiques."""
        charts_row = ctk.CTkFrame(self, fg_color="transparent")
        charts_row.pack(fill="x", pady=(0, 16))
        charts_row.grid_columnconfigure(0, weight=6)
        charts_row.grid_columnconfigure(1, weight=4)
        
        # Graphique linéaire
        line_card = FluentCard(charts_row, title="Trajets des 7 derniers jours")
        line_card.grid(row=0, column=0, sticky="ew", padx=(0, 12))
        
        fig = Figure(figsize=(6, 3), facecolor="none")
        ax = fig.add_subplot(111)
        
        try:
            is_dark = ctk.get_appearance_mode() == "Dark"
        except Exception:
            is_dark = False
        text_color = "#FFFFFF" if is_dark else "#1A1A1A"
        grid_color = "#3D3D3D" if is_dark else "#E5E5E5"
        
        ax.set_facecolor("none")
        fig.patch.set_alpha(0)
        
        jours = ["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"]
        trajets = [1820, 2150, 1980, 2380, 2640, 3100, 2890]
        
        ax.plot(jours, trajets, color="#1A3A6C", linewidth=2.5, marker="o",
                markersize=6, markerfacecolor="white", markeredgewidth=2)
        ax.fill_between(range(len(jours)), trajets, alpha=0.08, color="#1A3A6C")
        ax.set_xticks(range(len(jours)))
        ax.set_xticklabels(jours, color=text_color, fontsize=11)
        ax.tick_params(axis='y', colors=text_color, labelsize=11)
        ax.spines[:].set_visible(False)
        ax.grid(axis="y", color=grid_color, linewidth=0.5)
        ax.margins(x=0.02)
        
        canvas = FigureCanvasTkAgg(fig, master=line_card)
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=20, pady=(8, 20))
        canvas.draw()
        
        # Donut
        donut_card = FluentCard(charts_row, title="Modes de paiement")
        donut_card.grid(row=0, column=1, sticky="ew")
        
        fig2 = Figure(figsize=(4, 3), facecolor="none")
        ax2 = fig2.add_subplot(111)
        ax2.set_facecolor("none")
        fig2.patch.set_alpha(0)
        
        import mpatches as mpatches_lib
        sizes = [45, 35, 20]
        labels = ["MoovMoney", "Airtel Money", "Carte bancaire"]
        colors = ["#1A3A6C", "#009E60", "#FCD116"]
        
        wedges, texts, autotexts = ax2.pie(
            sizes, labels=None, colors=colors,
            autopct="%1.0f%%", startangle=90,
            wedgeprops=dict(width=0.6, edgecolor="none"),
            pctdistance=0.75
        )
        for t in autotexts:
            t.set_color(text_color)
            t.set_fontsize(10)
        
        patches = [mpatches_lib.Patch(color=c, label=l) for c, l in zip(colors, labels)]
        ax2.legend(handles=patches, loc="lower center", fontsize=9,
                   labelcolor=text_color, framealpha=0, ncol=1,
                   bbox_to_anchor=(0.5, -0.15))
        
        canvas2 = FigureCanvasTkAgg(fig2, master=donut_card)
        canvas2.get_tk_widget().pack(fill="both", expand=True, padx=20, pady=(8, 20))
        canvas2.draw()
    
    def _build_recent_activity(self):
        """Tableau d'activité récente."""
        activity_card = FluentCard(self, title="Activité récente")
        activity_card.pack(fill="x", pady=(0, 16))
        
        headers = ["Heure", "Événement", "Utilisateur", "Montant", "Statut"]
        rows = [
            ["14:32", "Paiement confirmé", "Client #4821", "1,500 XAF", "✅ Succès"],
            ["14:30", "Incident SOS", "Trip #9832",  "—",         "🚨 Ouvert"],
            ["14:28", "Nouveau conducteur", "Thomas M.", "—",      "⏳ En attente"],
            ["14:25", "Paiement confirmé", "Client #4819", "800 XAF",  "✅ Succès"],
            ["14:21", "Trajet terminé",    "Trip #9831",  "2,000 XAF", "✅ Terminé"],
        ]
        
        table_frame = ctk.CTkFrame(activity_card, fg_color="transparent")
        table_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        col_weights = [1, 3, 2, 2, 1]
        for i in range(5):
            table_frame.grid_columnconfigure(i, weight=col_weights[i])
        
        for j, header in enumerate(headers):
            ctk.CTkLabel(
                table_frame, text=header,
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color=("#9A9A9A", "#6D6D6D"),
                anchor="w"
            ).grid(row=0, column=j, sticky="ew", padx=8, pady=(0, 8))
        
        ctk.CTkFrame(table_frame, height=1, fg_color=("#E5E5E5", "#3D3D3D")).grid(
            row=1, column=0, columnspan=5, sticky="ew", pady=(0, 8)
        )
        
        for i, row in enumerate(rows):
            bg = ("white", "#2C2C2C") if i % 2 == 0 else ("#F9F9F9", "#333333")
            row_frame = ctk.CTkFrame(table_frame, fg_color=bg, corner_radius=8)
            row_frame.grid(row=i+2, column=0, columnspan=5, sticky="ew", pady=2)
            
            for j in range(5):
                row_frame.grid_columnconfigure(j, weight=col_weights[j])
            
            for j, cell in enumerate(row):
                ctk.CTkLabel(
                    row_frame, text=cell,
                    font=ctk.CTkFont(size=12),
                    text_color=("#374151", "#D1D5DB"),
                    anchor="w"
                ).grid(row=0, column=j, sticky="ew", padx=16, pady=10)
    
    def _refresh_data(self):
        """Rafraîchit les données."""
        from datetime import datetime
        self._last_update_label.configure(text=f"Mis à jour : {datetime.now().strftime('%H:%M:%S')}")
    
    def _schedule_refresh(self):
        """Programme le rafraîchissement automatique."""
        self._refresh_data()
        self.after(self._refresh_interval, self._schedule_refresh)