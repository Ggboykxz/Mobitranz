# ============================================================
# Module Transactions — Administration
# Fichier : desktop_admin/windows/modules/transactions_module.py
# ============================================================

import customtkinter as ctk
from tkinter import filedialog, messagebox
from datetime import datetime, timedelta
from desktop_admin.theme.components import FluentCard, KPICard, FluentButton


class TransactionsModule(ctk.CTkFrame):
    """Module de gestion des transactions."""
    
    kpi_callbacks = {
        "all": None,
        "success": None,
        "failed": None,
        "stats": None,
    }
    _current_filter = "all"
    _date_from = None
    _date_to = None
    _status_filter = "all"
    
    def __init__(self, master, user_data=None, dashboard=None, **kwargs):
        kwargs.setdefault("fg_color", "transparent")
        kwargs.pop("dashboard", None)
        kwargs.pop("user_data", None)
        super().__init__(master, **kwargs)
        
        self._dashboard = master
        self._setup_ui()
    
    def _setup_ui(self):
        """Configure l'interface utilisateur."""
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(0, 16))
        ctk.CTkLabel(header, text="Transactions",
            font=ctk.CTkFont(size=22, weight="bold"), text_color=("#1A1A1A", "white")).pack(side="left")
        
        self._kpi_cards = []
        kpi_frame = ctk.CTkFrame(self, fg_color="transparent")
        kpi_frame.pack(fill="x", pady=(0, 16))
        for i in range(4):
            kpi_frame.grid_columnconfigure(i, weight=1, uniform="kpi")
        
        kpis = [
            ("💰", "Total", "15.2M", "all", "#1A3A6C"),
            ("✅", "Réussies", "14.8M", "success", "#009E60"),
            ("❌", "Échouées", "320K", "failed", "#E53E3E"),
            ("📊", "Taux", "98.2%", "stats", "#7C3AED")
        ]
        
        for i, (icon, title, value, filter_key, accent) in enumerate(kpis):
            kpi = KPICard(kpi_frame, icon=icon, title=title, value=value, accent_color=accent)
            kpi.grid(row=0, column=i, sticky="ew", padx=(0, 12 if i < 3 else 0))
            kpi.bind("<Button-1>", lambda e, k=filter_key: self._on_kpi_click(k))
            kpi.configure(cursor="hand2")
            for child in kpi.winfo_children():
                child.configure(cursor="hand2")
            self._kpi_cards.append((kpi, filter_key))
        
        voir_plus_btn = FluentButton(kpi_frame, text="Voir plus →", variant="ghost", icon="📋")
        voir_plus_btn.grid(row=1, column=0, columnspan=4, sticky="e", pady=(12, 0))
        voir_plus_btn.configure(cursor="hand2")
        
        self._filter_frame = ctk.CTkFrame(self, fg_color="transparent")
        self._filter_frame.pack(fill="x", pady=(0, 16))
        
        self._date_from_entry = ctk.CTkEntry(
            self._filter_frame,
            placeholder_text="Du (JJ/MM/AAAA)",
            width=140,
        )
        self._date_from_entry.pack(side="left", padx=(0, 8))
        self._date_from_entry.insert(0, (datetime.now() - timedelta(days=30)).strftime("%d/%m/%Y"))
        
        self._date_to_entry = ctk.CTkEntry(
            self._filter_frame,
            placeholder_text="Au (JJ/MM/AAAA)",
            width=140,
        )
        self._date_to_entry.pack(side="left", padx=(0, 8))
        self._date_to_entry.insert(0, datetime.now().strftime("%d/%m/%Y"))
        
        self._status_combo = ctk.CTkComboBox(
            self._filter_frame,
            values=["Tous", "Réussies", "Échouées"],
            width=140,
            state="readonly"
        )
        self._status_combo.pack(side="left", padx=(0, 8))
        self._status_combo.set("Tous")
        
        self._apply_filter_btn = FluentButton(
            self._filter_frame,
            text="Filtrer",
            variant="secondary",
            icon="🔍",
        )
        self._apply_filter_btn.pack(side="left", padx=(0, 8))
        self._apply_filter_btn.bind("<Button-1>", lambda e: self._apply_filters())
        self._apply_filter_btn.configure(cursor="hand2")
        
        export_btn = FluentButton(
            self._filter_frame,
            text="Exporter",
            variant="success",
            icon="📥",
        )
        export_btn.pack(side="left")
        export_btn.bind("<Button-1>", lambda e: self._export_data())
        export_btn.configure(cursor="hand2")
        
        card = FluentCard(self, title="Historique des transactions")
        card.pack(fill="both", expand=True)
        self._content = ctk.CTkFrame(card, fg_color="transparent")
        self._content.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        headers = ["ID", "Montant", "Méthode", "Statut", "Date", "Client", " Actions"]
        header_frame = ctk.CTkFrame(self._content, fg_color=("#F3F4F6", "#2D3748"))
        header_frame.pack(fill="x", pady=(0, 8))
        for h in headers:
            align = "w" if h == "ID" else "e" if h == " Actions" else "center"
            ctk.CTkLabel(header_frame, text=h, font=ctk.CTkFont(size=12, weight="bold"),
                text_color=("#6B7280", "#9CA3AF"), anchor=align).pack(side="left", padx=16, pady=8)
        
        self._transaction_data = [
            {"id": "pay_001", "amount": "1,500", "method": "MoovMoney", "status": "success",
             "date": "25/04/2026 14:32", "client": {"name": "Konan Jean", "phone": "+225 07 12 34 56 78"},
             "driver": {"name": "Diabaté Mamadou", "phone": "+225 05 98 76 54 32"},
             "created": "25/04/2026 14:30:45", "updated": "25/04/2026 14:32:10"},
            {"id": "pay_002", "amount": "800", "method": "Airtel", "status": "success",
             "date": "25/04/2026 14:28", "client": {"name": "Traoré Fatou", "phone": "+225 01 23 45 67 89"},
             "driver": {"name": "Kouadio Paul", "phone": "+225 05 67 89 01 23"},
             "created": "25/04/2026 14:27:12", "updated": "25/04/2026 14:28:05"},
            {"id": "pay_003", "amount": "2,000", "method": "Carte", "status": "failed",
             "date": "25/04/2026 14:15", "client": {"name": "Ouattara Ali", "phone": "+225 05 44 33 22 11"},
             "driver": {"name": "Coulibaly Souleymane", "phone": "+225 07 88 99 00 11"},
             "created": "25/04/2026 14:14:33", "updated": "25/04/2026 14:15:22"},
            {"id": "pay_004", "amount": "3,500", "method": "OM", "status": "success",
             "date": "25/04/2026 14:02", "client": {"name": "Koffi René", "phone": "+225 02 11 22 33 44"},
             "driver": {"name": "Bamba Issouf", "phone": "+225 06 55 66 77 88"},
             "created": "25/04/2026 14:01:08", "updated": "25/04/2026 14:02:45"},
            {"id": "pay_005", "amount": "500", "method": "MoovMoney", "status": "failed",
             "date": "25/04/2026 13:45", "client": {"name": "Doumbia Awa", "phone": "+225 04 55 66 77 88"},
             "driver": {"name": "Fofana Yacouba", "phone": "+225 08 22 33 44 55"},
             "created": "25/04/2026 13:44:11", "updated": "25/04/2026 13:45:33"},
        ]
        
        self._rows_container = ctk.CTkFrame(self._content, fg_color="transparent")
        self._rows_container.pack(fill="both", expand=True)
        self._refresh_transaction_list()
        
        self._drawer = None
    
    def _on_kpi_click(self, filter_key):
        """Gère le clic sur une carte KPI."""
        self._current_filter = filter_key
        for card, key in self._kpi_cards:
            border_color = ("#1A3A6C", "#5B85CC") if key == filter_key else ("#E5E5E5", "#3D3D3D")
            card.configure(border_color=border_color)
        self._apply_filters()
    
    def _apply_filters(self):
        """Applique les filtres de date et de statut."""
        try:
            from_str = self._date_from_entry.get()
            to_str = self._date_to_entry.get()
            self._date_from = datetime.strptime(from_str, "%d/%m/%Y") if from_str.strip() else None
            self._date_to = datetime.strptime(to_str, "%d/%m/%Y") if to_str.strip() else None
        except ValueError:
            messagebox.showerror("Erreur", "Format de date invalide. Utilisez JJ/MM/AAAA")
            return
        
        status_map = {"Tous": "all", "Réussies": "success", "Échouées": "failed"}
        self._status_filter = status_map.get(self._status_combo.get(), "all")
        
        self._refresh_transaction_list()
    
    def _refresh_transaction_list(self):
        """Rafraîchit la liste des transactions."""
        for widget in self._rows_container.winfo_children():
            widget.destroy()
        
        filtered = self._transaction_data
        
        if self._current_filter == "success":
            filtered = [t for t in filtered if t["status"] == "success"]
        elif self._current_filter == "failed":
            filtered = [t for t in filtered if t["status"] == "failed"]
        
        if self._status_filter != "all":
            filtered = [t for t in filtered if t["status"] == self._status_filter]
        
        for t in filtered:
            self._add_transaction_row(t)
    
    def _add_transaction_row(self, transaction):
        """Ajoute une ligne de transaction cliquable."""
        status_color = ("#009E60", "#4DC882") if transaction["status"] == "success" else ("#E53E3E", "#FC8181")
        status_icon = "✅" if transaction["status"] == "success" else "❌"
        
        row = ctk.CTkFrame(self._rows_container, fg_color=("white", "#2C2C2C"), corner_radius=8)
        row.pack(fill="x", pady=2)
        row.configure(cursor="hand2")
        
        for child in row.winfo_children():
            child.configure(cursor="hand2")
        
        row.bind("<Button-1>", lambda e, t=transaction: self._show_detail_drawer(t))
        
        ctk.CTkLabel(row, text=transaction["id"], font=ctk.CTkFont(size=12), text_color=("#374151", "#D1D5DB"),
            anchor="w", width=100).pack(side="left", padx=16, pady=10)
        ctk.CTkLabel(row, text=f"{transaction['amount']} €", font=ctk.CTkFont(size=12), text_color=("#374151", "#D1D5DB"),
            anchor="center").pack(side="left", padx=16, pady=10)
        ctk.CTkLabel(row, text=transaction["method"], font=ctk.CTkFont(size=12), text_color=("#374151", "#D1D5DB"),
            anchor="center").pack(side="left", padx=16, pady=10)
        
        status_badge = ctk.CTkLabel(row, text=status_icon, font=ctk.CTkFont(size=14), text_color=status_color,
            fg_color=status_color, corner_radius=6, padx=8, pady=2)
        status_badge.pack(side="left", padx=16, pady=10)
        
        ctk.CTkLabel(row, text=transaction["date"], font=ctk.CTkFont(size=12), text_color=("#374151", "#D1D5DB"),
            anchor="center").pack(side="left", padx=16, pady=10)
        ctk.CTkLabel(row, text=transaction["client"]["name"], font=ctk.CTkFont(size=12), text_color=("#374151", "#D1D5DB"),
            anchor="center").pack(side="left", padx=16, pady=10)
        
        ctk.CTkButton(row, text="👁", width=32, height=32, fg_color="transparent", hover_color=("#F0F0F0", "#3D3D3D"),
            command=lambda t=transaction: self._show_detail_drawer(t)).pack(side="right", padx=(0, 8))
        
        row.transaction_data = transaction
    
    def _show_detail_drawer(self, transaction):
        """Affiche le drawer de détails."""
        if self._drawer:
            self._close_detail_drawer()
        
        self._drawer = ctk.CTkToplevel(self)
        self._drawer.title(f"Détails - {transaction['id']}")
        self._drawer.geometry("500x700")
        self._drawer.resizable(False, False)
        
        screen_width = self._drawer.winfo_screenwidth()
        screen_height = self._drawer.winfo_screenheight()
        x = screen_width - 520
        y = (screen_height - 720) // 2
        self._drawer.geometry(f"500x700+{x}+{y}")
        
        self._drawer.attributes("-topmost", True)
        
        drawer = FluentCard(self._drawer, title=f"Transaction {transaction['id']}", padding=20)
        drawer.pack(fill="both", expand=True, padx=10, pady=10)
        
        content = ctk.CTkFrame(drawer, fg_color="transparent")
        content.pack(fill="both", expand=True)
        
        status_color = ("#009E60", "#4DC882") if transaction["status"] == "success" else ("#E53E3E", "#FC8181")
        status_text = "Réussie" if transaction["status"] == "success" else "Échouée"
        
        ctk.CTkLabel(content, text=f"Montant: {transaction['amount']} €",
            font=ctk.CTkFont(size=18, weight="bold")).pack(anchor="w", pady=(0, 8))
        ctk.CTkLabel(content, text=f"Méthode: {transaction['method']}",
            font=ctk.CTkFont(size=14)).pack(anchor="w", pady=(0, 4))
        ctk.CTkLabel(content, text=f"Statut: {status_text}", font=ctk.CTkFont(size=14),
            text_color=status_color).pack(anchor="w", pady=(0, 16))
        
        ctk.CTkLabel(content, text="─" * 40, text_color=("#6B7280", "#9CA3AF")) .pack(anchor="w", pady=8)
        
        ctk.CTkLabel(content, text="Informations Client", font=ctk.CTkFont(size=14, weight="bold")) .pack(anchor="w", pady=(8, 4))
        ctk.CTkLabel(content, text=f"Nom: {transaction['client']['name']}",
            font=ctk.CTkFont(size=12)).pack(anchor="w", pady=2)
        ctk.CTkLabel(content, text=f"Téléphone: {transaction['client']['phone']}",
            font=ctk.CTkFont(size=12)).pack(anchor="w", pady=2)
        
        ctk.CTkLabel(content, text="─" * 40, text_color=("#6B7280", "#9CA3AF")) .pack(anchor="w", pady=8)
        
        ctk.CTkLabel(content, text="Informations Chauffeur", font=ctk.CTkFont(size=14, weight="bold")) .pack(anchor="w", pady=(8, 4))
        ctk.CTkLabel(content, text=f"Nom: {transaction['driver']['name']}",
            font=ctk.CTkFont(size=12)).pack(anchor="w", pady=2)
        ctk.CTkLabel(content, text=f"Téléphone: {transaction['driver']['phone']}",
            font=ctk.CTkFont(size=12)).pack(anchor="w", pady=2)
        
        ctk.CTkLabel(content, text="─" * 40, text_color=("#6B7280", "#9CA3AF")) .pack(anchor="w", pady=8)
        
        ctk.CTkLabel(content, text="Horodatages", font=ctk.CTkFont(size=14, weight="bold")) .pack(anchor="w", pady=(8, 4))
        ctk.CTkLabel(content, text=f"Créé le: {transaction['created']}",
            font=ctk.CTkFont(size=12)).pack(anchor="w", pady=2)
        ctk.CTkLabel(content, text=f"Modifié le: {transaction['updated']}",
            font=ctk.CTkFont(size=12)).pack(anchor="w", pady=2)
        
        close_btn = FluentButton(content, text="Fermer", variant="secondary", icon="✕")
        close_btn.pack(anchor="e", pady=(20, 0))
        close_btn.bind("<Button-1>", lambda e: self._close_detail_drawer())
        close_btn.configure(cursor="hand2")
        
        self._drawer.protocol("WM_DELETE_WINDOW", self._close_detail_drawer)
        self._drawer.transient(self)
        self._drawer.grab_set_global()
    
    def _close_detail_drawer(self):
        """Ferme le drawer de détails."""
        if self._drawer:
            self._drawer.destroy()
            self._drawer = None
    
    def _export_data(self):
        """Exporte les données filtrées vers un fichier CSV."""
        filtered = self._transaction_data
        
        if self._current_filter == "success":
            filtered = [t for t in filtered if t["status"] == "success"]
        elif self._current_filter == "failed":
            filtered = [t for t in filtered if t["status"] == "failed"]
        
        if self._status_filter != "all":
            filtered = [t for t in filtered if t["status"] == self._status_filter]
        
        if not filtered:
            messagebox.showwarning("Attention", "Aucune donnée à exporter avec les filtres actuels.")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialfile=f"transactions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        )
        
        if not file_path:
            return
        
        try:
            import csv
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['ID', 'Montant (€)', 'Méthode', 'Statut', 'Date', 'Client', 'Téléphone Client', 'Chauffeur', 'Téléphone Chauffeur', 'Créé le', 'Modifié le'])
                
                for t in filtered:
                    writer.writerow([
                        t['id'], t['amount'], t['method'], t['status'], t['date'],
                        t['client']['name'], t['client']['phone'],
                        t['driver']['name'], t['driver']['phone'],
                        t['created'], t['updated']
                    ])
            
            messagebox.showinfo("Succès", f"Données exportées vers:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Erreur", f"Échec de l'export: {str(e)}")