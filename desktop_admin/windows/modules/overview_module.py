# ============================================================
# Module Vue d'ensemble — Dashboard principal
# Fichier : desktop_admin/windows/modules/overview_module.py
# Description : KPIs temps reel, graphiques, activite recente
# ============================================================

import customtkinter as ctk
from desktop_admin.theme.components import KPICard, FluentCard, FluentButton
from desktop_admin.windows.theme.ui_theme import UITheme, get_palette, font, title_font, body_font
from datetime import datetime, timedelta
import random


class OverviewModule(ctk.CTkFrame):
    """Module tableau de bord principal — Vue d'ensemble MobiTranz."""
    
    def __init__(self, master, user_data=None, dashboard=None, **kwargs):
        kwargs.setdefault("fg_color", "transparent")
        super().__init__(master, **kwargs)
        
        self._user_data = user_data or {}
        self._dashboard = dashboard
        self._pal = get_palette()
        
        self._build_header()
        self._build_stats_cards()
        self._build_kpi_row()
        self._build_charts_row()
        self._build_recent_activity()
        self._build_quick_actions()
        
        UITheme.set_mode("Dark")
    
    def _get_colors(self):
        """Get current theme colors."""
        return get_palette()
    
    def _build_header(self):
        pal = self._get_colors()
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(0, 20))
        
        hour = datetime.now().hour
        greeting = "Bonjour" if 5 <= hour < 12 else "Bon apres-midi" if 12 <= hour < 18 else "Bonsoir"
        email = self._user_data.get("email", "Admin")
        
        title_frame = ctk.CTkFrame(header, fg_color="transparent")
        title_frame.pack(side="left")
        
        ctk.CTkLabel(
            title_frame,
            text=f"{greeting}, {email.split('@')[0].capitalize()} !",
            font=title_font(28),
            text_color=pal["primary"],
        ).pack(anchor="w")
        
        ctk.CTkLabel(
            title_frame,
            text=f"Voici l'activite de MobiTranz en temps reel — {datetime.now().strftime('%d/%m/%Y')}",
            font=body_font(13),
            text_color=pal["text_secondary"],
        ).pack(anchor="w", pady=(4, 0))
        
        right_frame = ctk.CTkFrame(header, fg_color="transparent")
        right_frame.pack(side="right")
        
        ctk.CTkLabel(
            right_frame,
            text=f"🕐 {datetime.now().strftime('%H:%M:%S')}",
            font=body_font(12),
            text_color=pal["text_muted"],
        ).pack(side="left", padx=12)
        
        self._refresh_btn = ctk.CTkButton(
            right_frame, text="🔄 Actualiser",
            fg_color=pal["primary"], hover_color=pal["primary_hover"],
            text_color="white", height=36,
            font=body_font(13), command=self._refresh_data
        )
        self._refresh_btn.pack(side="left")
    
    def _refresh_data(self):
        """Refresh all data."""
        self._pal = get_palette()
        for widget in self.winfo_children():
            widget.destroy()
        self._build_header()
        self._build_stats_cards()
        self._build_kpi_row()
        self._build_charts_row()
        self._build_recent_activity()
        self._build_quick_actions()
    
    def _build_stats_cards(self):
        pal = self._get_colors()
        stats_frame = ctk.CTkFrame(self, fg_color="transparent")
        stats_frame.pack(fill="x", pady=(0, 16))
        
        for i in range(4):
            stats_frame.grid_columnconfigure(i, weight=1)
        
        stats = [
            ("🚗", "Vehicules actifs", f"{random.randint(120, 150)}", "98% en service"),
            ("👨‍✈️", "Conducteurs", f"{random.randint(200, 280)}", f"{random.randint(85, 95)}% disponibles"),
            ("📱", "Utilisateurs", f"{random.randint(5000, 15000)}", f"+{random.randint(50, 200)} aujourd'hui"),
            ("💳", "Transactions", f"{random.randint(800, 1500)}", f"{random.randint(95, 99)}% reussies"),
        ]
        
        for i, (icon, title, value, subtitle) in enumerate(stats):
            card = ctk.CTkFrame(
                stats_frame,
                fg_color=pal["card_bg"],
                border_color=pal["card_border"],
                border_width=1,
                corner_radius=12
            )
            card.grid(row=0, column=i, sticky="ew", padx=8)
            
            ctk.CTkLabel(card, text=icon, font=ctk.CTkFont(size=24)).pack(pady=(16, 8))
            
            ctk.CTkLabel(
                card, text=title,
                font=body_font(12),
                text_color=pal["text_secondary"],
            ).pack()
            
            ctk.CTkLabel(
                card, text=value,
                font=title_font(24),
                text_color=pal["primary"],
            ).pack()
            
            ctk.CTkLabel(
                card, text=subtitle,
                font=body_font(11),
                text_color=pal["success"],
            ).pack(pady=(0, 16))
    
    def _build_kpi_row(self):
        pal = self._get_colors()
        kpi_frame = ctk.CTkFrame(self, fg_color="transparent")
        kpi_frame.pack(fill="x", pady=(0, 16))
        
        for i in range(4):
            kpi_frame.grid_columnconfigure(i, weight=1)
        
        kpis = [
            ("🚗", "Trajets aujourd'hui", f"{random.randint(800, 1200)}", "+12%", pal["primary"]),
            ("💰", "Revenus du jour", f"{random.randint(2000000, 3500000):,} XAF", f"+{random.randint(8, 25)}%", pal["success"]),
            ("⭐", "Note moyenne", f"{random.uniform(4.2, 4.8):.1f}/5", "+0.2", pal["accent_yellow"]),
            ("🚨", "Incidents", f"{random.randint(0, 8)}", f"{random.randint(-50, -10)}%", pal["danger"]),
        ]
        
        for i, (icon, title, value, trend, color) in enumerate(kpis):
            card = ctk.CTkFrame(
                kpi_frame,
                fg_color=pal["card_bg"],
                border_color=pal["card_border"],
                border_width=1,
                corner_radius=12,
            )
            card.grid(row=0, column=i, sticky="ew", padx=8)
            card.configure(cursor="hand2")
            
            icon_label = ctk.CTkLabel(card, text=icon, font=ctk.CTkFont(size=20))
            icon_label.pack(pady=(16, 8))
            
            ctk.CTkLabel(
                card, text=title,
                font=body_font(12),
                text_color=pal["text_secondary"],
            ).pack()
            
            ctk.CTkLabel(
                card, text=value,
                font=title_font(20),
                text_color=pal["text"],
            ).pack()
            
            ctk.CTkLabel(
                card, text=f"📈 {trend}",
                font=body_font(11),
                text_color=color,
            ).pack(pady=(0, 16))
    
    def _build_charts_row(self):
        pal = self._get_colors()
        charts_row = ctk.CTkFrame(self, fg_color="transparent")
        charts_row.pack(fill="x", pady=(0, 16))
        charts_row.grid_columnconfigure(0, weight=2)
        charts_row.grid_columnconfigure(1, weight=1)
        
        card1 = ctk.CTkFrame(
            charts_row,
            fg_color=pal["card_bg"],
            border_color=pal["card_border"],
            border_width=1,
            corner_radius=12,
        )
        card1.grid(row=0, column=0, sticky="ew", padx=(0, 12))
        
        ctk.CTkLabel(
            card1, text="📊 Trajets cette semaine",
            font=title_font(16),
            text_color=pal["text"],
        ).pack(anchor="w", padx=20, pady=16)
        
        days = ["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"]
        values = [random.randint(500, 1500) for _ in range(7)]
        max_val = max(values)
        
        chart_frame = ctk.CTkFrame(card1, fg_color="transparent")
        chart_frame.pack(fill="both", expand=True, padx=20, pady=(0, 16))
        
        bar_w = 0.6
        spacing = (1 - bar_w) / (len(days) + 1)
        
        for i, (day, val) in enumerate(zip(days, values)):
            x = spacing + i * (bar_w + spacing)
            h_pct = val / max_val
            
            bar_frameInner = ctk.CTkFrame(chart_frame, fg_color="transparent")
            bar_frameInner.place(relx=x, rely=0.9, relwidth=bar_w, relheight=0.8, anchor="sw")
            
            bar = ctk.CTkFrame(
                bar_frameInner,
                fg_color=pal["primary"],
                corner_radius=4
            )
            bar.pack(fill="y", pady=(0, 4))
            bar.pack_propagate(False)
            bar.configure(height=int(200 * h_pct))
            
            ctk.CTkLabel(
                bar_frameInner, text=f"{val}",
                font=body_font(10, weight="bold"),
                text_color=pal["primary"],
            ).pack(pady=(0, 4))
            
            ctk.CTkLabel(
                chart_frame, text=day,
                font=body_font(10),
                text_color=pal["text_secondary"],
            ).place(relx=x + bar_w/2, rely=1.0, anchor="s")
        
        card2 = ctk.CTkFrame(
            charts_row,
            fg_color=pal["card_bg"],
            border_color=pal["card_border"],
            border_width=1,
            corner_radius=12,
        )
        card2.grid(row=0, column=1, sticky="ew")
        
        ctk.CTkLabel(
            card2, text="💳 Repartition paiements",
            font=title_font(16),
            text_color=pal["text"],
        ).pack(anchor="w", padx=20, pady=16)
        
        payment_data = [
            ("MoovMoney", 45, "#1A3A6C"),
            ("Airtel", 35, "#10B981"),
            ("Carte", 20, "#FCD116"),
        ]
        
        for name, pct, color in payment_data:
            row = ctk.CTkFrame(card2, fg_color="transparent")
            row.pack(fill="x", padx=20, pady=8)
            
            ctk.CTkLabel(
                row, text=name,
                font=body_font(12),
                text_color=pal["text"],
            ).pack(side="left")
            
            bar_bg = ctk.CTkFrame(
                row,
                fg_color=pal["input_bg"],
                height=8,
                corner_radius=4
            )
            bar_bg.pack(side="left", fill="x", expand=True, padx=12)
            bar_bg.pack_propagate(False)
            
            bar = ctk.CTkFrame(bar_bg, fg_color=color, height=8, corner_radius=4)
            bar.pack(side="left", ipadx=int(pct * 3))
            
            ctk.CTkLabel(
                row, text=f"{pct}%",
                font=body_font(12, weight="bold"),
                text_color=color
            ).pack(side="right")
    
    def _build_recent_activity(self):
        pal = self._get_colors()
        activity_card = ctk.CTkFrame(
            self,
            fg_color=pal["card_bg"],
            border_color=pal["card_border"],
            border_width=1,
            corner_radius=12,
        )
        activity_card.pack(fill="x", pady=(0, 16))
        
        ctk.CTkLabel(
            activity_card, text="⚡ Activite recente",
            font=title_font(16),
            text_color=pal["text"],
        ).pack(anchor="w", padx=20, pady=16)
        
        headers = ["Heure", "Type", "Description", "Montant", "Statut"]
        
        header_frame = ctk.CTkFrame(activity_card, fg_color=pal["input_bg"], corner_radius=8)
        header_frame.pack(fill="x", padx=20, pady=(0, 8))
        
        for h in headers:
            ctk.CTkLabel(
                header_frame, text=h,
                font=body_font(11, weight="bold"),
                text_color=pal["text_secondary"],
            ).pack(side="left", padx=8, pady=8)
        
        activities = [
            ("14:32", "Paiement", "Trajet #4821 - Owendo -> PK12", "1,500 XAF", "✅ Succes"),
            ("14:28", "Inscription", "Nouveau client +24107 XXX XX XX", "—", "✅ Valide"),
            ("14:15", "Incident", "SOS - Trajet #4819", "—", "🚨 En cours"),
            ("13:45", "Paiement", "Trajet #4818 - Libreville Centre", "2,000 XAF", "✅ Succes"),
            ("13:22", "Vehicule", "AA-002-BK - Mise a jour position", "—", "✅ OK"),
            ("12:58", "Conducteur", "Validation KYC - Jean M.", "—", "⏳ En attente"),
        ]
        
        for i, (heure, type_, desc, montant, statut) in enumerate(activities):
            row = ctk.CTkFrame(
                activity_card,
                fg_color=pal["surface_hover"] if i % 2 == 0 else pal["surface"],
                corner_radius=8
            )
            row.pack(fill="x", padx=20, pady=4)
            
            ctk.CTkLabel(
                row, text=heure,
                font=body_font(11),
                text_color=pal["text_muted"],
                width=60
            ).pack(side="left", padx=8, pady=12)
            
            status_color = {
                "Paiement": pal["primary"],
                "Inscription": pal["success"],
                "Incident": pal["danger"],
                "Vehicule": pal["accent_yellow"],
                "Conducteur": pal["accent_purple"]
            }
            ctk.CTkLabel(
                row, text=type_,
                font=body_font(11, weight="bold"),
                text_color=(status_color.get(type_, pal["text_secondary"]), pal["text_secondary"]),
                width=100
            ).pack(side="left", padx=8)
            
            ctk.CTkLabel(
                row, text=desc,
                font=body_font(11),
                text_color=pal["text"],
            ).pack(side="left", padx=8, fill="x", expand=True)
            
            ctk.CTkLabel(
                row, text=montant,
                font=body_font(11),
                text_color=pal["success"],
                width=100
            ).pack(side="left", padx=8)
            
            stat_ok = "Succes" in statut or "Valide" in statut or "OK" in statut
            ctk.CTkLabel(
                row, text=statut,
                font=body_font(11),
                text_color=pal["success"] if stat_ok else pal["danger"],
            ).pack(side="left", padx=8)
    
    def _build_quick_actions(self):
        pal = self._get_colors()
        actions_card = ctk.CTkFrame(
            self,
            fg_color=pal["card_bg"],
            border_color=pal["card_border"],
            border_width=1,
            corner_radius=12,
        )
        actions_card.pack(fill="x")
        
        ctk.CTkLabel(
            actions_card, text="⚡ Actions rapides",
            font=title_font(16),
            text_color=pal["text"],
        ).pack(anchor="w", padx=20, pady=16)
        
        actions_frame = ctk.CTkFrame(actions_card, fg_color="transparent")
        actions_frame.pack(fill="x", padx=20, pady=(0, 16))
        
        actions = [
            ("➕", "Nouveau client", pal["success"]),
            ("🚗", "Ajouter conducteur", pal["primary"]),
            ("📊", "Generer rapport", pal["accent_purple"]),
            ("🔔", "Notifications", pal["accent_yellow"]),
            ("⚙️", "Parametres", pal["text_secondary"]),
        ]
        
        for icon, label, color in actions:
            btn = ctk.CTkButton(
                actions_frame,
                text=f"{icon} {label}",
                fg_color=color, hover_color=color,
                height=40,
                font=body_font(13),
                command=lambda l=label: self._quick_action(l)
            )
            btn.pack(side="left", padx=8, fill="x", expand=True)
    
    def _quick_action(self, action):
        print(f"Quick action: {action}")