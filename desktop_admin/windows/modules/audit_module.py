# ============================================================
# Module Audit — Administration
# Fichier : desktop_admin/windows/modules/audit_module.py
# ============================================================

import customtkinter as ctk
from desktop_admin.theme.components import FluentCard, KPICard
from datetime import datetime


class AuditModule(ctk.CTkFrame):
    """Module de sécurité et logs."""
    
    def __init__(self, master, user_data=None, dashboard=None, **kwargs):
        kwargs.setdefault("fg_color", "transparent")
        kwargs.pop("dashboard", None)
        kwargs.pop("user_data", None)
        super().__init__(master, **kwargs)
        
        self._logs = [
            {"timestamp": "14:32:15", "action": "LOGIN", "user": "admin@mobitranz.ga", "ip": "41.78.123.45", "status": "✅", "details": "Connexion réussie depuis le panneau admin"},
            {"timestamp": "14:28:03", "action": "PAYMENT_INITIATED", "user": "client_456", "ip": "41.78.123.46", "status": "✅", "details": "Paiement de 150000 XOF initiated"},
            {"timestamp": "14:15:22", "action": "USER_SUSPENDED", "user": "admin@mobitranz.ga", "ip": "41.78.123.45", "status": "✅", "details": "Compte utilisateur suspendu pour activité suspecte"},
            {"timestamp": "13:45:11", "action": "LOGIN_FAILED", "user": "unknown", "ip": "41.78.123.50", "status": "❌", "details": "Échec de connexion - mot de passe incorrect"},
            {"timestamp": "13:30:45", "action": "IP_BLOCKED", "user": "system", "ip": "41.78.123.50", "status": "🚫", "details": "IP bloquée après 3 tentatives échouées"},
            {"timestamp": "13:15:00", "action": "PASSWORD_RESET", "user": "user@test.com", "ip": "41.78.123.47", "status": "✅", "details": "Mot de passe réinitialisé avec succès"},
            {"timestamp": "12:50:22", "action": "ANOMALY_DETECTED", "user": "system", "ip": "41.78.123.60", "status": "⚠️", "details": "Activité inhabituelle détectée - multiple connexions simultanées"},
            {"timestamp": "12:30:10", "action": "LOGIN_FAILED", "user": "hacker@test.com", "ip": "41.78.123.70", "status": "❌", "details": "Tentative de connexion suspecte"},
        ]
        self._active_filter = None
        
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(0, 16))
        ctk.CTkLabel(header, text="Sécurité & Logs",
            font=ctk.CTkFont(size=22, weight="bold"), text_color=("#1A1A1A", "white")).pack(side="left")
        
        self._build_filters(header)
        
        kpi_frame = ctk.CTkFrame(self, fg_color="transparent")
        kpi_frame.pack(fill="x", pady=(0, 16))
        for i in range(4):
            kpi_frame.grid_columnconfigure(i, weight=1, uniform="kpi")
        
        self.kpi_login = KPICard(kpi_frame, icon="🔒", title="Connexions", value="1,247")
        self.kpi_login.grid(row=0, column=0, sticky="ew", padx=(0, 12))
        
        self.kpi_failed = self._create_clickable_kpi(kpi_frame, "⚠️", "Tentatives échouées", "12", "LOGIN_FAILED", row=0, column=1)
        self.kpi_blocked = self._create_clickable_kpi(kpi_frame, "🚫", "IPs bloquées", "3", "IP_BLOCKED", row=0, column=2)
        self.kpi_anomaly = self._create_clickable_kpi(kpi_frame, "⚡", "Anomalies", "1", "ANOMALY_DETECTED", row=0, column=3)
        
        self.card = FluentCard(self, title="Journal d'audit récent")
        self.card.pack(fill="both", expand=True)
        content = ctk.CTkFrame(self.card, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        self.header_frame = ctk.CTkFrame(content, fg_color=("#F3F4F6", "#2D3748"))
        self.header_frame.pack(fill="x", pady=(0, 8))
        
        headers = ["Horodatage", "Action", "Utilisateur", "IP ", "Statut"]
        for h in headers:
            ctk.CTkLabel(self.header_frame, text=h, font=ctk.CTkFont(size=12, weight="bold"),
                text_color=("#6B7280", "#9CA3AF")).pack(side="left", padx=16, pady=8)
        
        self.logs_container = ctk.CTkFrame(content, fg_color="transparent")
        self.logs_container.pack(fill="both", expand=True)
        
        self._render_logs()
        
        self._build_footer(content)
    
    def _build_filters(self, parent):
        filter_frame = ctk.CTkFrame(parent, fg_color="transparent")
        filter_frame.pack(side="right")
        
        ctk.CTkLabel(filter_frame, text="Filtrer:", 
            font=ctk.CTkFont(size=12),
            text_color=("#6B7280", "#9CA3AF")).pack(side="left", padx=(0, 8))
        
        self.filter_action = ctk.CTkComboBox(filter_frame, values=["Toutes les actions", "LOGIN", "LOGIN_FAILED", "IP_BLOCKED", "ANOMALY_DETECTED", "PAYMENT_INITIATED", "PASSWORD_RESET", "USER_SUSPENDED"], width=150)
        self.filter_action.pack(side="left", padx=4)
        self.filter_action.bind("<<ComboboxSelected>>", lambda e: self._apply_filters())
        
        self.filter_user = ctk.CTkEntry(filter_frame, placeholder_text="Utilisateur", width=120)
        self.filter_user.pack(side="left", padx=4)
        self.filter_user.bind("<KeyRelease>", lambda e: self._apply_filters())
        
        self.filter_date = ctk.CTkEntry(filter_frame, placeholder_text="Date (JJ/MM)", width=100)
        self.filter_date.pack(side="left", padx=4)
        self.filter_date.bind("<KeyRelease>", lambda e: self._apply_filters())
        
        self.filter_ip = ctk.CTkEntry(filter_frame, placeholder_text="Adresse IP", width=100)
        self.filter_ip.pack(side="left", padx=4)
        self.filter_ip.bind("<KeyRelease>", lambda e: self._apply_filters())
        
        clear_btn = ctk.CTkButton(filter_frame, text="✕", width=30, command=self._clear_filters)
        clear_btn.pack(side="left", padx=4)
    
    def _create_clickable_kpi(self, parent, icon, title, value, filter_value, row, column):
        card = KPICard(parent, icon=icon, title=title, value=value)
        card.grid(row=row, column=column, sticky="ew", padx=(0, 12))
        
        card.bind("<Button-1>", lambda e, fv=filter_value: self._on_kpi_click(fv))
        for child in card.winfo_children():
            child.bind("<Button-1>", lambda e, fv=filter_value: self._on_kpi_click(fv))
            child.configure(cursor="hand2")
        
        return card
    
    def _on_kpi_click(self, filter_value):
        self._active_filter = filter_value
        self.filter_action.set(filter_value)
        self._apply_filters()
    
    def _apply_filters(self):
        action_val = self.filter_action.get()
        user_val = self.filter_user.get().strip().lower()
        date_val = self.filter_date.get().strip()
        ip_val = self.filter_ip.get().strip()
        
        filtered = self._logs
        
        if action_val and action_val != "Toutes les actions":
            filtered = [l for l in filtered if l["action"] == action_val]
        
        if user_val:
            filtered = [l for l in filtered if user_val in l["user"].lower()]
        
        if date_val:
            filtered = [l for l in filtered if date_val in l["timestamp"]]
        
        if ip_val:
            filtered = [l for l in filtered if ip_val in l["ip"]]
        
        self._render_logs(filtered)
    
    def _clear_filters(self):
        self.filter_action.set("Toutes les actions")
        self.filter_user.delete(0, "end")
        self.filter_date.delete(0, "end")
        self.filter_ip.delete(0, "end")
        self._active_filter = None
        self._render_logs()
    
    def _render_logs(self, logs=None):
        for widget in self.logs_container.winfo_children():
            widget.destroy()
        
        display_logs = logs if logs is not None else self._logs
        
        for log in display_logs:
            row = ctk.CTkFrame(self.logs_container, fg_color=("white", "#2C2C2C"), corner_radius=8)
            row.pack(fill="x", pady=2)
            row.configure(cursor="hand2")
            
            row.bind("<Button-1>", lambda e, l=log: self._show_log_details(l))
            for child in row.winfo_children():
                child.bind("<Button-1>", lambda e, l=log: self._show_log_details(l))
                child.configure(cursor="hand2")
            
            ctk.CTkLabel(row, text=log["timestamp"], font=ctk.CTkFont(size=12), 
                text_color=("#374151", "#D1D5DB")).pack(side="left", padx=16, pady=10)
            ctk.CTkLabel(row, text=log["action"], font=ctk.CTkFont(size=12), 
                text_color=("#374151", "#D1D5DB")).pack(side="left", padx=16, pady=10)
            ctk.CTkLabel(row, text=log["user"], font=ctk.CTkFont(size=12), 
                text_color=("#374151", "#D1D5DB")).pack(side="left", padx=16, pady=10)
            ctk.CTkLabel(row, text=log["ip"], font=ctk.CTkFont(size=12), 
                text_color=("#374151", "#D1D5DB")).pack(side="left", padx=16, pady=10)
            ctk.CTkLabel(row, text=log["status"], font=ctk.CTkFont(size=12), 
                text_color=("#374151", "#D1D5DB")).pack(side="left", padx=16, pady=10)
    
    def _show_log_details(self, log):
        details_win = ctk.CTkToplevel(self)
        details_win.title(f"Détails du log - {log['action']}")
        details_win.geometry("500x350")
        details_win.transient(self)
        details_win.grab_set()
        
        main_frame = ctk.CTkFrame(details_win, fg_color=("white", "#1E1E1E"))
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        title = ctk.CTkLabel(main_frame, text=f"Log: {log['action']}", 
            font=ctk.CTkFont(size=18, weight="bold"), text_color=("#1A1A1A", "white"))
        title.pack(anchor="w", pady=(0, 20))
        
        fields = [
            ("Horodatage", log["timestamp"]),
            ("Action", log["action"]),
            ("Utilisateur", log["user"]),
            ("Adresse IP", log["ip"]),
            ("Statut", log["status"]),
            ("Détails", log["details"]),
        ]
        
        for label, value in fields:
            row = ctk.CTkFrame(main_frame, fg_color="transparent")
            row.pack(fill="x", pady=8)
            
            ctk.CTkLabel(row, text=f"{label}:", font=ctk.CTkFont(size=12, weight="bold"),
                text_color=("#6B7280", "#9CA3AF"), width=100, anchor="w").pack(side="left")
            
            ctk.CTkLabel(row, text=value, font=ctk.CTkFont(size=12),
                text_color=("#1A1A1A", "white"), anchor="w").pack(side="left", fill="x", expand=True)
        
        close_btn = ctk.CTkButton(main_frame, text="Fermer", command=details_win.destroy)
        close_btn.pack(anchor="e", pady=(20, 0))
    
    def _build_footer(self, parent):
        footer = ctk.CTkFrame(parent, fg_color="transparent")
        footer.pack(fill="x", pady=(16, 0))
        
        see_more_btn = ctk.CTkButton(footer, text="Voir plus →", command=self._see_more,
            fg_color=("#1A3A6C", "#2563EB"), hover_color=("#1E40AF", "#1D4ED8"))
        see_more_btn.pack(side="right")
    
    def _see_more(self):
        print("Voir plus clicked - afficher historique complet")